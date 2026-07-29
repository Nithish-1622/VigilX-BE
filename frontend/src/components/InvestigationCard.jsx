import React from 'react'
import InvestigationHeader from './investigation/InvestigationHeader'
import InvestigationOverview from './investigation/InvestigationOverview'
import QueryInterpretationCard from './investigation/QueryInterpretationCard'
import GeneratedQueryBlock from './investigation/GeneratedQueryBlock'
import AgentExecutionGrid from './investigation/AgentExecutionGrid'
import BackendToolsGrid from './investigation/BackendToolsGrid'
import EvidenceSummaryMatrix from './investigation/EvidenceSummaryMatrix'
import IntelligenceReportSection from './investigation/IntelligenceReportSection'
import EntityBadgesGroup from './investigation/EntityBadgesGroup'
import DynamicVisualizationPanel from './investigation/DynamicVisualizationPanel'
import RecommendedActionsGroup from './investigation/RecommendedActionsGroup'
import FollowUpQuestionChips from './investigation/FollowUpQuestionChips'
import ExecutionMetadataFooter from './investigation/ExecutionMetadataFooter'

export default function InvestigationCard({ data = {}, onSelectPrompt }) {
  const metadata = data.metadata || {}

  return (
    <div style={{
      width: '100%',
      maxWidth: 760,
      background: 'var(--bg-panel)',
      border: '1px solid var(--border-base)',
      borderRadius: 4,
      overflow: 'hidden',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
    }}>
      {/* 1. Header & Threat Level */}
      <InvestigationHeader
        responseId={data.response_id}
        confidence={data.confidence || 0.88}
        confidenceLabel={data.confidence_label || 'high'}
        criticPassed={data.critic_passed !== false}
      />

      {/* 2. Overview & Intent Strategy */}
      <InvestigationOverview
        intent={data.intent}
        complexity={data.complexity}
        userQuery={metadata.user_query}
      />

      {/* 3. Query Interpretation & Extracted Entities */}
      <QueryInterpretationCard
        metadata={metadata}
        intent={data.intent}
      />

      {/* 4. Generated Retrieval Query (SQL + Vector) */}
      <GeneratedQueryBlock
        metadata={metadata}
      />

      {/* 5. Executed AI Agents Grid */}
      <AgentExecutionGrid
        agentsExecuted={metadata.agents_executed}
        metadata={metadata}
      />

      {/* 6. Backend Tools Used Grid */}
      <BackendToolsGrid
        toolsUsed={metadata.tools_used}
        metadata={metadata}
      />

      {/* 7. Evidence Summary Matrix */}
      <EvidenceSummaryMatrix
        evidenceBundle={data.evidence_bundle}
      />

      {/* 8. Crime Intelligence Report (Executive Summary & Findings) */}
      <IntelligenceReportSection
        executiveSummary={data.executive_summary}
        keyFindings={data.key_findings || []}
        criticPassed={data.critic_passed !== false}
        criticWarnings={data.critic_warnings || []}
      />

      {/* 9. Identified Case Entities */}
      <EntityBadgesGroup
        relatedEntities={data.related_entities || []}
      />

      {/* 10. Dynamic Visualizations (Timeline & Network) */}
      <DynamicVisualizationPanel
        timeline={data.timeline || []}
        chartSpecs={data.chart_specs || []}
      />

      {/* 11. Recommended Investigative Actions */}
      <RecommendedActionsGroup
        recommendations={data.recommendations || []}
      />

      {/* 12. Suggested Follow-Up Prompt Chips */}
      <FollowUpQuestionChips
        onSelectPrompt={onSelectPrompt}
      />

      {/* 13. Execution Metadata Footer */}
      <ExecutionMetadataFooter
        metadata={metadata}
        criticPassed={data.critic_passed !== false}
        sessionId={data.session_id}
        responseId={data.response_id}
      />
    </div>
  )
}
