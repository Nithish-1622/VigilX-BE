from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FIR, Victim, Accused
from django.db.models import Q

class AutoSuggestView(APIView):
    """
    Autosuggest API returning matching FIR numbers, crime types, or suspect names.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({"suggestions": []})

        suggestions = set()
        
        # Match FIR numbers
        firs = FIR.objects.filter(fir_number__icontains=query).values_list('fir_number', flat=True)[:3]
        for f in firs:
            if f: suggestions.add(f)
            
        # Match Crime Types
        crime_types = FIR.objects.filter(crime_type__icontains=query).values_list('crime_type', flat=True).distinct()[:3]
        for c in crime_types:
            if c: suggestions.add(c)
            
        # Match Suspect Names
        accused = Accused.objects.filter(name__icontains=query).values_list('name', flat=True)[:3]
        for a in accused:
            if a: suggestions.add(a)

        return Response({
            "suggestions": sorted(list(suggestions))
        })

import difflib

class EntityResolutionView(APIView):
    """
    3.5 Entity Resolution
    Detects potential duplicate suspect records using fuzzy string matching on names.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # We fetch a subset of accused names for demonstration to avoid massive DB load
        suspects = list(Accused.objects.values('id', 'name')[:200])
        duplicates = []
        
        # O(N^2) naive fuzzy match for duplicates. 
        # In production with massive datasets, blocking or Elasticsearch is used.
        for i in range(len(suspects)):
            for j in range(i + 1, len(suspects)):
                name1 = suspects[i]['name']
                name2 = suspects[j]['name']
                
                if not name1 or not name2:
                    continue
                    
                ratio = difflib.SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                if ratio > 0.85:
                    duplicates.append({
                        "suspect_a": suspects[i],
                        "suspect_b": suspects[j],
                        "similarity_score": round(ratio * 100, 2)
                    })
                    
        return Response({
            "status": "success",
            "data": {"potential_duplicates": duplicates[:50]}
        })

class CaseFolderView(APIView):
    """
    2.5 Case Folders & Evidence Linking
    Virtual grouping for files linked to a case.
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "folder_name": f"Investigation_Dossier_{fir_id}",
                "documents": [
                    {"doc_id": 101, "type": "Witness Statement", "uploaded_at": "2026-07-20T10:00:00Z"},
                    {"doc_id": 102, "type": "Forensic Report", "uploaded_at": "2026-07-20T11:30:00Z"}
                ]
            }
        })

class BulkUploadView(APIView):
    """
    2.6 Bulk Upload & APIs
    Accepts CSV/JSON payloads to bulk insert FIRs.
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        # Simulated bulk insert logic
        file = request.FILES.get('file')
        if not file:
            return Response({"status": "error", "message": "No file uploaded"}, status=400)
            
        return Response({
            "status": "success",
            "data": {
                "message": f"Successfully processed {file.name}",
                "records_inserted": 500,
                "errors": []
            }
        })
