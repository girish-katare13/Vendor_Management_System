from rest_framework import generics, status
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer
from django.db.models import Count, Avg, Sum, F
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated  

# Create your views here.

class VendorListView(generics.ListCreateAPIView):
    # List and create view for vendors
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  

class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete view for a specific vendor
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  

class PurchaseOrderListView(generics.ListCreateAPIView):
    # List and create view for purchase orders
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated] 

class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete view for a specific purchase order
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  

class VendorPerformanceView(generics.RetrieveAPIView):
    # Retrieve view for vendor performance metrics
    queryset = Vendor.objects.all()
    serializer_class = HistoricalPerformanceSerializer
    lookup_field = 'pk'
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  

    def retrieve(self, request, *args, **kwargs):
        # Retrieve the vendor
        vendor = self.get_object()

        # Calculate performance metrics
        on_time_delivery_rate = self.calculate_on_time_delivery_rate(vendor)
        quality_rating_avg = self.calculate_quality_rating_avg(vendor)
        average_response_time = self.calculate_average_response_time(vendor)
        fulfillment_rate = self.calculate_fulfillment_rate(vendor)

        # Create or update the historical performance record
        HistoricalPerformance.objects.create(
            vendor=vendor,
            on_time_delivery_rate=on_time_delivery_rate,
            quality_rating_avg=quality_rating_avg,
            average_response_time=average_response_time,
            fulfillment_rate=fulfillment_rate,
        )

        # Return the calculated performance metrics
        data = {
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating_avg': quality_rating_avg,
            'average_response_time': average_response_time,
            'fulfillment_rate': fulfillment_rate,
        }

        return Response(data, status=status.HTTP_200_OK)

    def calculate_on_time_delivery_rate(self, vendor):
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        total_completed_pos = completed_pos.count()

        if total_completed_pos == 0:
            return 0.0

        on_time_deliveries = completed_pos.filter(delivery_date__lte=timezone.now())
        on_time_delivery_rate = (on_time_deliveries.count() / total_completed_pos) * 100.0

        return round(on_time_delivery_rate, 2)

    def calculate_quality_rating_avg(self, vendor):
        completed_pos_with_rating = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False)
        total_completed_pos_with_rating = completed_pos_with_rating.count()

        if total_completed_pos_with_rating == 0:
            return 0.0

        quality_rating_avg = completed_pos_with_rating.aggregate(avg_quality=Avg('quality_rating'))['avg_quality']
        return round(quality_rating_avg, 2)

    def calculate_average_response_time(self, vendor):
        acknowledged_pos = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False)
        total_acknowledged_pos = acknowledged_pos.count()

        if total_acknowledged_pos == 0:
            return 0.0

        response_times = acknowledged_pos.annotate(response_time=Avg(F('acknowledgment_date') - F('issue_date')))
        average_response_time = response_times.aggregate(Avg('response_time'))['response_time__avg']

        return round(average_response_time.total_seconds() / 60, 2)

    def calculate_fulfillment_rate(self, vendor):
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        total_pos = completed_pos.count()

        if total_pos == 0:
            return 0.0

        fulfilled_pos = completed_pos.exclude(issue_date__gt=F('acknowledgment_date'))
        fulfillment_rate = (fulfilled_pos.count() / total_pos) * 100.0

        return round(fulfillment_rate, 2)
