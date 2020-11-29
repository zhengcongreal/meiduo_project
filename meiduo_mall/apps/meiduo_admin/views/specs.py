from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPUSpecification, SpecificationOption
from apps.meiduo_admin.serializers.specs import SPUSpecificationSerializer, SPUSpecificationOptionsSerializer, \
    SPUSpecSerializer
from apps.meiduo_admin.utils import PageNum


class SPUSpecsModelViewSet(ModelViewSet):
    serializer_class =SPUSpecificationSerializer
    pagination_class = PageNum

    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SPUSpecification.objects.all()
        else:
            return SPUSpecification.objects.filter(name__contains=keyword)

class SPUSpecsOptionsModelViewSet(ModelViewSet):
    serializer_class =SPUSpecificationOptionsSerializer
    queryset = SpecificationOption.objects.all()
    pagination_class = PageNum


class SPUSpecListView(ListAPIView):
    serializer_class = SPUSpecSerializer
    queryset =SPUSpecification.objects.all()



