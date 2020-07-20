from rest_framework.serializers import PrimaryKeyRelatedField, ManyRelatedField
from rest_framework.relations import MANY_RELATION_KWARGS
from rest_framework.fields import get_attribute


class ManyRelatedFilterField(ManyRelatedField):
    def __init__(self, filters=None, *args, **kwargs):
        self.filters = filters
        super(ManyRelatedFilterField, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        # Can't have any relationships if not created
        if hasattr(instance, 'pk') and instance.pk is None:
            return []

        relationship = get_attribute(instance, self.source_attrs)

        filters = self.filters

        if isinstance(relationship, list) and filters:
            rst = []
            for obj in relationship:
                for k, v in filters.items():
                    if getattr(obj, k) != v:
                        break
                else:
                    rst.append(obj)
            return rst

        if hasattr(relationship, 'filter') and filters:
            return relationship.filter(**filters)
        elif hasattr(relationship, 'all'):
            return relationship.all()
        else:
            return relationship


class PrimaryKeyRelatedFilterField(PrimaryKeyRelatedField):
    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'filters': kwargs.pop('filters', None), 'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedFilterField(**list_kwargs)
