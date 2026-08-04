from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ml_studio.config import ml_settings
from ml_studio.schemas.job import JobReportResponse, TrainingJob


@dataclass(frozen=True)
class ReportArtifacts:
    report_dir: Path
    json_path: Path
    html_path: Path
    pdf_path: Path
    meta_path: Path


def _artifacts(job_id: str) -> ReportArtifacts:
    report_dir = Path(ml_settings.reports_store_path) / job_id
    return ReportArtifacts(
        report_dir=report_dir,
        json_path=report_dir / "report.json",
        html_path=report_dir / "report.html",
        pdf_path=report_dir / "report.pdf",
        meta_path=report_dir / "meta.json",
    )


def build_canonical_report(job: TrainingJob) -> JobReportResponse:
    preprocessing = job.preprocessing_report or {}
    evaluation = job.eval_scores or {}
    benchmark = job.benchmark_result or {}

    recommendations: list[str] = []
    token_stats = preprocessing.get("token_stats") if isinstance(preprocessing, dict) else None
    if isinstance(token_stats, dict) and token_stats.get("exceeds_max_len_count"):
        recommendations.append("Some samples exceed max sequence length. Consider increasing max_seq_length or truncation strategy.")

    if job.config and getattr(job.config, "max_steps", 0) and job.loss is not None and job.loss > 1.0:
        recommendations.append("Final loss is relatively high. Consider increasing training steps or adjusting learning rate.")

    if isinstance(preprocessing, dict) and preprocessing.get("cleaned_rows_count", 0) < 50:
        recommendations.append("Dataset is small. Consider synthetic augmentation before retraining.")

    summary: dict[str, Any] = {
        "job_id": job.job_id,
        "tenant_id": getattr(job, "tenant_id", "default"),
        "job_name": job.job_name,
        "status": job.status.value,
        "dataset_id": job.config.dataset_id if job.config else None,
        "base_model": job.config.base_model if job.config else None,
        "training_strategy": job.config.training_strategy if job.config else None,
        "progress": job.progress,
        "current_step": job.current_step,
        "total_steps": job.total_steps,
        "final_loss": job.loss,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "approved_by": job.approved_by,
        "approved_at": job.approved_at.isoformat() if job.approved_at else None,
        "model_id": job.model_id,
        "ollama_model_name": job.ollama_model_name,
    }

    return JobReportResponse(
        summary=summary,
        pipeline_stage_results=job.pipeline_stage_results or {},
        evaluation=evaluation,
        benchmark=benchmark,
        recommendations=recommendations,
    )


def generate_report_artifacts(job: TrainingJob) -> dict[str, Any]:
    art = _artifacts(job.job_id)
    art.report_dir.mkdir(parents=True, exist_ok=True)

    report = build_canonical_report(job)
    art.json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    html_ok = True
    html_error: str | None = None
    try:
        html = render_report_html(report.model_dump(mode="json"))
        art.html_path.write_text(html, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        html_ok = False
        html_error = str(exc)[:500]

    pdf_ok = True
    pdf_error: str | None = None
    try:
        if art.html_path.exists():
            generate_pdf_from_html(art.html_path, art.pdf_path)
        else:
            raise RuntimeError("HTML report missing; cannot build PDF.")
    except Exception as exc:  # noqa: BLE001
        pdf_ok = False
        pdf_error = str(exc)[:500]

    meta = {
        "job_id": job.job_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "json_path": str(art.json_path),
        "html_path": str(art.html_path),
        "pdf_path": str(art.pdf_path),
        "html_ok": html_ok,
        "html_error": html_error,
        "pdf_ok": pdf_ok,
        "pdf_error": pdf_error,
    }
    art.meta_path.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    return meta


def render_report_html(report: dict[str, Any]) -> str:
    try:
        from jinja2 import Environment, BaseLoader

        template = Environment(loader=BaseLoader(), autoescape=True).from_string(_REPORT_TEMPLATE)
        return template.render(report=report)
    except Exception:
        return _render_report_html_fallback(report)


def generate_pdf_from_html(html_path: Path, pdf_path: Path) -> None:
    from weasyprint import HTML  # type: ignore

    HTML(filename=str(html_path)).write_pdf(str(pdf_path))


def _render_report_html_fallback(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    recs = report.get("recommendations", [])
    eval_ = report.get("evaluation", {})
    bench = report.get("benchmark", {})

    def _kv(d: dict[str, Any]) -> str:
        rows = []
        for k, v in d.items():
            rows.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
        return "\n".join(rows)

    rec_items = "\n".join(f"<li>{r}</li>" for r in recs)

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>ML Studio Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 18px; }}
    td, th {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f4f4f4; text-align: left; }}
    h2 {{ margin-top: 28px; }}
  </style>
</head>
<body>
  <h1>Training Report</h1>
  <h2>Summary</h2>
  <table><tbody>{_kv(summary)}</tbody></table>
  <h2>Evaluation</h2>
  <table><tbody>{_kv(eval_)}</tbody></table>
  <h2>Benchmark</h2>
  <table><tbody>{_kv(bench)}</tbody></table>
  <h2>Recommendations</h2>
  <ul>{rec_items}</ul>
</body>
</html>
"""


_REPORT_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>ML Studio Training Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 18px; }
    td, th { border: 1px solid #ddd; padding: 8px; }
    th { background: #f4f4f4; text-align: left; }
    h2 { margin-top: 28px; }
    .muted { color: #666; font-size: 12px; }
  </style>
</head>
<body>
  <h1>Training Report</h1>
  <div class="muted">Generated by VigilX ML Studio</div>

  <h2>Summary</h2>
  <table>
    <tbody>
    {% for k, v in report.summary.items() %}
      <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
    {% endfor %}
    </tbody>
  </table>

  <h2>Evaluation</h2>
  <table>
    <tbody>
    {% for k, v in report.evaluation.items() %}
      <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
    {% endfor %}
    </tbody>
  </table>

  <h2>Benchmark</h2>
  <table>
    <tbody>
    {% for k, v in report.benchmark.items() %}
      <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
    {% endfor %}
    </tbody>
  </table>

  <h2>Recommendations</h2>
  <ul>
    {% for r in report.recommendations %}
      <li>{{ r }}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""
