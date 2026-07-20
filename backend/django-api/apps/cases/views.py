from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .models import FIR, Victim, Accused, ClueEntity
from api.serializers.cases import (
    FIRSerializer, FIRDetailSerializer, 
    VictimSerializer, AccusedSerializer, ClueEntitySerializer
)
from api.permissions.rbac import IsCaseWriteAuthorized, DenyPolicymakerPII

class FIRViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage FIR (First Information Reports) case records.
    Read access is allowed for all authenticated roles.
    Write access is restricted to Investigators and Supervisors.
    Supports robust search (on FIR number and description) and filters.
    """
    permission_classes = [IsAuthenticated, IsCaseWriteAuthorized]
    def get_serializer_class(self):
        return FIRDetailSerializer

    def get_queryset(self):
        queryset = FIR.objects.all().order_by('-reported_date_time')
        
        # Extract query parameters
        status_val = self.request.query_params.get('status')
        crime_type_val = self.request.query_params.get('crime_type')
        officer_id = self.request.query_params.get('officer_id')
        date_start = self.request.query_params.get('date_start')
        date_end = self.request.query_params.get('date_end')
        search_query = self.request.query_params.get('search')
        fir_id_val = self.request.query_params.get('fir_id')
        
        # Apply filters programmatically
        if status_val:
            queryset = queryset.filter(status=status_val)
        if crime_type_val:
            queryset = queryset.filter(crime_type=crime_type_val)
        if officer_id:
            queryset = queryset.filter(officer_in_charge_id=officer_id)
        if date_start:
            queryset = queryset.filter(incident_date_time__gte=date_start)
        if date_end:
            queryset = queryset.filter(incident_date_time__lte=date_end)
        if fir_id_val:
            import uuid
            try:
                uuid.UUID(fir_id_val)
                queryset = queryset.filter(Q(fir_number=fir_id_val) | Q(id=fir_id_val))
            except ValueError:
                queryset = queryset.filter(fir_number=fir_id_val)
        if search_query:
            q_objects = Q()
            stop_words = {'give', 'details', 'about', 'what', 'who', 'show', 'tell', 'find', 'search', 'suspect', 'accused', 'victim', 'case', 'fir', 'number', 'the', 'and', 'for', 'with', 'from', 'this', 'that'}
            for word in search_query.split():
                if len(word) > 2 and word.lower() not in stop_words:
                    q_objects &= (
                        Q(fir_number__icontains=word) | 
                        Q(description__icontains=word) |
                        Q(accused__name__icontains=word) |
                        Q(victims__name__icontains=word) |
                        Q(complainants__name__icontains=word)
                    )
            if q_objects:
                queryset = queryset.filter(q_objects).distinct()
            
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "status": "success",
            "message": "FIR created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "status": "success",
            "message": "FIR updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class VictimViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage victims.
    Access is completely blocked for Policymakers.
    Write access is restricted to Investigators and Supervisors.
    """
    serializer_class = VictimSerializer
    permission_classes = [IsAuthenticated, DenyPolicymakerPII, IsCaseWriteAuthorized]

    def get_queryset(self):
        queryset = Victim.objects.all().order_by('-created_at')

        name_val = self.request.query_params.get('name')
        fir_val = self.request.query_params.get('fir')
        search_query = self.request.query_params.get('search')

        if name_val:
            queryset = queryset.filter(name__icontains=name_val)

        if fir_val:
            import uuid
            try:
                uuid.UUID(fir_val)
                queryset = queryset.filter(fir_id=fir_val)
            except ValueError:
                queryset = queryset.filter(fir__fir_number=fir_val)

        if search_query:
            q_objects = Q()
            stop_words = {
                'give', 'details', 'about', 'what', 'who', 'show',
                'tell', 'find', 'search', 'suspect', 'accused',
                'victim', 'case', 'fir', 'number', 'the',
                'and', 'for', 'with', 'from', 'this', 'that'
            }

            for word in search_query.split():
                if len(word) > 2 and word.lower() not in stop_words:
                    q_objects &= Q(name__icontains=word)

            if q_objects:
                queryset = queryset.filter(q_objects)

        return queryset

class AccusedViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage accused and suspect records.
    Access is completely blocked for Policymakers.
    Write access is restricted to Investigators and Supervisors.
    """
    serializer_class = AccusedSerializer
    permission_classes = [IsAuthenticated, DenyPolicymakerPII, IsCaseWriteAuthorized]

    def get_queryset(self):
        queryset = Accused.objects.all().order_by('-created_at')

        name_val = self.request.query_params.get('name')
        fir_val = self.request.query_params.get('fir')
        search_query = self.request.query_params.get('search')

        if name_val:
            queryset = queryset.filter(name__icontains=name_val)

        if fir_val:
            import uuid
            try:
                uuid.UUID(fir_val)
                queryset = queryset.filter(fir_id=fir_val)
            except ValueError:
                queryset = queryset.filter(fir__fir_number=fir_val)

        if search_query:
            q_objects = Q()
            stop_words = {
                'give', 'details', 'about', 'what', 'who', 'show',
                'tell', 'find', 'search', 'suspect', 'accused',
                'victim', 'case', 'fir', 'number', 'the',
                'and', 'for', 'with', 'from', 'this', 'that'
            }

            for word in search_query.split():
                if len(word) > 2 and word.lower() not in stop_words:
                    q_objects &= Q(name__icontains=word)

            if q_objects:
                queryset = queryset.filter(q_objects)

        return queryset
class ClueEntityViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage case entities (phone numbers, vehicles, bank accounts).
    Write access is restricted to Investigators and Supervisors.
    Supports a custom matching interface for search endpoints.
    """
    queryset = ClueEntity.objects.all().order_by('-id')
    serializer_class = ClueEntitySerializer
    permission_classes = [IsAuthenticated, IsCaseWriteAuthorized]

    def list(self, request, *args, **kwargs):
        entity_type = request.query_params.get('entity_type')
        value = request.query_params.get('value')
        
        # If searching for matching cases linked by entities (e.g. phone / vehicle)
        if entity_type and value:
            matching_entities = ClueEntity.objects.filter(
                entity_type=entity_type, 
                value=value
            ).select_related('fir')
            
            matching_cases = []
            for item in matching_entities:
                matching_cases.append({
                    "fir_id": item.fir.id,
                    "fir_number": item.fir.fir_number,
                    "crime_type": item.fir.crime_type,
                    "status": item.fir.status,
                    "context": item.description
                })
            
            return Response({
                "status": "success",
                "data": {
                    "entity_type": entity_type,
                    "value": value,
                    "matching_cases": matching_cases
                }
            }, status=status.HTTP_200_OK)
            
        return super().list(request, *args, **kwargs)

# Refreshed import path structures and hosts
