from rest_framework import serializers
from .models import Master, Sketch, Style, Client, Session


class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ['id', 'name', 'expirience_years', 'hourly_rate']


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = ['id', 'title', 'description']


class SketchSerializer(serializers.ModelSerializer):
    master = MasterSerializer(read_only=True)
    master_id = serializers.PrimaryKeyRelatedField(queryset=Master.objects.all(), source='master', write_only=True)
    style = StyleSerializer(read_only=True)
    style_id = serializers.PrimaryKeyRelatedField(queryset=Style.objects.all(), source='style', write_only=True)
    
    class Meta:
        model = Sketch
        fields = ['id', 'title', 'master', 'master_id', 'style', 'style_id', 'is_available']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'phone_number']


class SessionSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), source='client', write_only=True)
    master = MasterSerializer(read_only=True)
    master_id = serializers.PrimaryKeyRelatedField(queryset=Master.objects.all(), source='master', write_only=True)
    sketch = SketchSerializer(read_only=True)
    sketch_id = serializers.PrimaryKeyRelatedField(queryset=Sketch.objects.all(), source='sketch', write_only=True)

    class Meta:
        model = Session
        fields = ['id', 'client', 'client_id', 'master', 'master_id', 'sketch', 'sketch_id', 'date', 'time', 'status']
