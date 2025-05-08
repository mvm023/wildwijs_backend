from rest_framework import viewsets
from ..biodiversity_api import *
from ..image_scrape_api import *
from ..serializers.admin_serializers import *
from ..permissions import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from knox.auth import TokenAuthentication
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

class QuizCategoryAdminAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if pk is not None:
            category = self.get_object(pk)
            if category is None:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = QuizCategoryAdminSerializer(category)
            return Response(serializer.data)

        # Otherwise return the full list
        categories = QuizCategory.objects.all()
        serializer = QuizCategoryAdminSerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Create a new quiz category"""
        serializer = QuizCategoryAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        """Retrieve a single quiz category by ID"""
        try:
            return QuizCategory.objects.get(pk=pk)
        except QuizCategory.DoesNotExist:
            return None

    def put(self, request, pk, *args, **kwargs):
        """Update an existing quiz category"""
        category = self.get_object(pk)
        if category is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizCategoryAdminSerializer(category, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        """Partially update an existing quiz category"""
        category = self.get_object(pk)
        if category is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizCategoryAdminSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """Delete a quiz category"""
        category = self.get_object(pk)
        if category is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuizSubcategoryAdminAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if pk is not None:
            subcategory = self.get_object(pk)
            if subcategory is None:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = QuizSubcategoryAdminSerializer(subcategory)
            return Response(serializer.data)

        # Otherwise return the full list
        subcategories = QuizSubcategory.objects.all()
        serializer = QuizSubcategoryAdminSerializer(subcategories, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Create a new quiz category"""
        serializer = QuizSubcategoryAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        """Retrieve a single quiz category by ID"""
        try:
            return QuizSubcategory.objects.get(pk=pk)
        except QuizSubcategory.DoesNotExist:
            return None

    def put(self, request, pk, *args, **kwargs):
        """Update an existing quiz category"""
        subcategory = self.get_object(pk)
        if subcategory is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizSubcategoryAdminSerializer(subcategory, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        """Partially update an existing quiz category"""
        subcategory = self.get_object(pk)
        if subcategory is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizSubcategoryAdminSerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """Delete a quiz category"""
        subcategory = self.get_object(pk)
        if subcategory is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        subcategory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class QuizLayerAdminViewSet(viewsets.ModelViewSet):
    queryset = QuizLayer.objects.all()
    serializer_class = QuizLayerAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]

class QuizAdminViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]


