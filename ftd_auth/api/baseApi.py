# Python
# Django
# Rest Framework
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
# Local

class BaseApi(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'])
    def getFilters(self, request, **kwargs):
        try:
            key_list = []
            filters = self.filterset_class.get_filters()
            for key, value in filters.items():
                key_list.append(key)
            return Response({"filters": key_list})
        except:
            return Response({"filters": []})