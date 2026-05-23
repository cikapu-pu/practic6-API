from django.shortcuts import render

from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from .models import Master, Sketch, Style, Client, Session
from .serializers import MasterSerializer, SketchSerializer, StyleSerializer, ClientSerializer, SessionSerializer
from .permissions import SketchPermission


class MasterViewSet(viewsets.ModelViewSet):
    serializer_class = MasterSerializer
    queryset = Master.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по имени мастера
    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        return qs
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного мастера на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового мастера
    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Частичное обновление (PATCH)
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Master.objects.get(pk=item['id']) for item in request.data]
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких мастеров
    def destroy(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        if ids:
            ids_list = [int(pk) for pk in ids.split(',')]
            Master.objects.filter(id__in=ids_list).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
        

class StyleViewSet(viewsets.ModelViewSet):
    serializer_class = StyleSerializer
    queryset = Style.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по названию стиля
    def get_queryset(self):
        qs = super().get_queryset()
        title = self.request.query_params.get('title')
        if title:
            qs = qs.filter(title__icontains=title)
        return qs
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного стиля на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового стиля
    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Частичное обновление (PATCH)
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Style.objects.get(pk=item['id']) for item in request.data]
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких стилей
    def destroy(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        if ids:
            ids_list = [int(pk) for pk in ids.split(',')]
            Style.objects.filter(id__in=ids_list).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
        

class SketchViewSet(viewsets.ModelViewSet):
    serializer_class = SketchSerializer
    queryset = Sketch.objects.all()
    permission_classes = [SketchPermission]

    # Переопределяем метод, чтобы добавить фильтрацию по имени наброска
    def get_queryset(self):
        qs = super().get_queryset()
        title = self.request.query_params.get('title')
        master_id = self.request.query_params.get('master_id')
        if title:
            qs = qs.filter(title__icontains=title)
        if master_id:
            qs = qs.filter(master_id=master_id)
        return qs
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного наброска на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового наброска
    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Частичное обновление (PATCH)
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Sketch.objects.get(pk=item['id']) for item in request.data]
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких набросков
    def destroy(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        if ids:
            ids_list = [int(pk) for pk in ids.split(',')]
            Sketch.objects.filter(id__in=ids_list).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)
       

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по названию клиента
    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        return qs
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного клиента на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового клиента
    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Частичное обновление (PATCH)
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Client.objects.get(pk=item['id']) for item in request.data]
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких клиентов
    def destroy(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        if ids:
            ids_list = [int(pk) for pk in ids.split(',')]
            Client.objects.filter(id__in=ids_list).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
        

class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по названию сессии
    def get_queryset(self):
        qs = super().get_queryset()
        master_id = self.request.query_params.get('master_id')
        client_id = self.request.query_params.get('client_id')
        sketch_id = self.request.query_params.get('sketch_id')
        if master_id:
            qs = qs.filter(master_id=master_id)
        if client_id:
            qs = qs.filter(client_id=client_id)
        if sketch_id:
            qs = qs.filter(sketch_id=sketch_id)
        return qs
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одной сессии на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание новой сессии
    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Частичное обновление (PATCH)
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Session.objects.get(pk=item['id']) for item in request.data]
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких сессий
    def destroy(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        if ids:
            ids_list = [int(pk) for pk in ids.split(',')]
            Session.objects.filter(id__in=ids_list).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
