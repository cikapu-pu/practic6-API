from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from .models import Master, Sketch, Style, Client, Session
from .serializers import MasterSerializer, SketchSerializer, StyleSerializer, ClientSerializer, SessionSerializer
from .permissions import SketchPermission


class MasterViewSet(viewsets.ModelViewSet):
    """Представление для работы с мастерами.

    Поддерживает все CRUD-операции, включая массовое создание,
    обновление и удаление. GET-запросы на детальный просмотр кешируются на 15 минут.
    Фильтрация списка возможна по GET-параметру `name` (поиск по подстроке).
    """

    # Указываем, что для преобразования объектов в JSON и обратно используется MasterSerializer
    serializer_class = MasterSerializer
    # Определяем базовый набор записей: все объекты модели Master
    queryset = Master.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по имени мастера
    def get_queryset(self):
        # Вызываем родительский метод, получая стандартный queryset
        qs = super().get_queryset()
        # Берём из параметров строки запроса значение по ключу 'name'
        name = self.request.query_params.get('name')
        # Если клиент передал имя, отбираем только тех мастеров, чьё имя содержит эту подстроку (без учёта регистра)
        if name:
            qs = qs.filter(name__icontains=name)
        # Возвращаем отфильтрованный (или исходный) queryset
        return qs
    
    def list(self, request, *args, **kwargs):
        # Просто вызываем родительскую реализацию — она вернёт список мастеров в JSON
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного мастера на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        # Родительский retrieve извлекает объект по id и отдаёт его данные
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового мастера (или нескольких)
    def create(self, request, *args, **kwargs):
        # Проверяем, является ли тело запроса списком (массовое создание) или одиночным объектом
        many = isinstance(request.data, list)
        # Создаём сериализатор: если many=True, то он ожидает список объектов
        serializer = self.get_serializer(data=request.data, many=many)
        # Запускаем валидацию, при ошибке автоматически вернётся ответ 400 с деталями
        serializer.is_valid(raise_exception=True)
        # Сохраняем новые объекты в базе
        self.perform_create(serializer)
        # Собираем заголовки ответа, например Location для созданного ресурса
        headers = self.get_success_headers(serializer.data)
        # Отдаём сериализованные данные с HTTP-статусом 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Полное обновление (PUT) одного или списка мастеров
    def update(self, request, *args, **kwargs):
        # Снова определяем, массовая операция или нет
        many = isinstance(request.data, list)
        if many:
            # Для списка из каждого элемента извлекаем id и находим соответствующий объект в базе
            instances = [Master.objects.get(pk=item['id']) for item in request.data]
            # Создаём сериализатор с найденными объектами и новыми данными, many=True
            serializer = self.get_serializer(instances, data=request.data, many=True)
        else:
            # Для одиночного объекта получаем его стандартным методом (по id из URL)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
        # Валидируем данные
        serializer.is_valid(raise_exception=True)
        # Сохраняем изменения
        self.perform_update(serializer)
        # Возвращаем обновлённые данные
        return Response(serializer.data)

    # Частичное обновление (PATCH) — работает как update, но с partial=True
    def partial_update(self, request, *args, **kwargs):
        # Проверяем структуру входящих данных
        many = isinstance(request.data, list)
        if many:
            # Извлекаем объекты из БД по переданным ID для массового обновления
            instances = [Master.objects.get(pk=item['id']) for item in request.data]
            # Обратите внимание: partial=True разрешает опускать обязательные поля при изменении списка
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            # Получаем один изменяемый объект по ID из URL-адреса
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        # Проверяем корректность переданных полей
        serializer.is_valid(raise_exception=True)
        # Фиксируем изменения в базе данных
        self.perform_update(serializer)
        # Возвращаем обновлённый JSON-объект
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких мастеров
    def destroy(self, request, *args, **kwargs):
        # Проверяем, передан ли GET-параметр ids
        ids = request.query_params.get('ids')
        if ids:
            # Разбиваем строку с id (например, "1,2,3") на список целых чисел
            ids_list = [int(pk) for pk in ids.split(',')]
            # Удаляем всех мастеров, чьи id попали в этот список
            Master.objects.filter(id__in=ids_list).delete()
            # Возвращаем 204 No Content — стандартный ответ успешного удаления
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Если ids нет, вызываем стандартный destroy, который удаляет одного мастера по id из URL
            return super().destroy(request, *args, **kwargs)
        

class StyleViewSet(viewsets.ModelViewSet):
    """Представление для работы со стилями татуировок.

    Поддерживает все CRUD-операции, включая массовое создание,
    обновление и удаление. GET-запросы на детальный просмотр кешируются на 15 минут.
    Фильтрация списка возможна по GET-параметру `title` (поиск по подстроке).
    """

    # Указываем, что для преобразования объектов в JSON и обратно используется StyleSerializer
    serializer_class = StyleSerializer
    # Определяем базовый набор записей: все объекты модели Style
    queryset = Style.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по названию стиля
    def get_queryset(self):
        # Вызываем родительский метод, получая стандартный queryset
        qs = super().get_queryset()
        # Берём из параметров строки запроса значение по ключу 'title'
        title = self.request.query_params.get('title')
        # Если клиент передал название, отбираем только те стили, чьё название содержит эту подстроку (без учёта регистра)
        if title:
            qs = qs.filter(title__icontains=title)
        # Возвращаем отфильтрованный (или исходный) queryset
        return qs
    
    def list(self, request, *args, **kwargs):
        # Просто вызываем родительскую реализацию — она вернёт список стилей в JSON
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного стиля на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        # Родительский retrieve извлекает объект по id и отдаёт его данные
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового стиля (или нескольких)
    def create(self, request, *args, **kwargs):
        # Проверяем, является ли тело запроса списком (массовое создание) или одиночным объектом
        many = isinstance(request.data, list)
        # Создаём сериализатор: если many=True, то он ожидает список объектов
        serializer = self.get_serializer(data=request.data, many=many)
        # Запускаем валидацию, при ошибке автоматически вернётся ответ 400 с деталями
        serializer.is_valid(raise_exception=True)
        # Сохраняем новые объекты в базе
        self.perform_create(serializer)
        # Собираем заголовки ответа, например Location для созданного ресурса
        headers = self.get_success_headers(serializer.data)
        # Отдаём сериализованные данные с HTTP-статусом 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Полное обновление (PUT) одного или списка стилей
    def update(self, request, *args, **kwargs):
        # Снова определяем, массовая операция или нет
        many = isinstance(request.data, list)
        if many:
            # Для списка из каждого элемента извлекаем id и находим соответствующий объект в базе
            instances = [Style.objects.get(pk=item['id']) for item in request.data]
            # Создаём сериализатор с найденными объектами и новыми данными, many=True
            serializer = self.get_serializer(instances, data=request.data, many=True)
        else:
            # Для одиночного объекта получаем его стандартным методом (по id из URL)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
        # Валидируем данные
        serializer.is_valid(raise_exception=True)
        # Сохраняем изменения
        self.perform_update(serializer)
        # Возвращаем обновлённые данные
        return Response(serializer.data)

    # Частичное обновление (PATCH) — работает как update, но с partial=True
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Style.objects.get(pk=item['id']) for item in request.data]
            # Обратите внимание: partial=True разрешает опускать обязательные поля
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких стилей
    def destroy(self, request, *args, **kwargs):
        # Проверяем, передан ли GET-параметр ids
        ids = request.query_params.get('ids')
        if ids:
            # Разбиваем строку с id (например, "1,2,3") на список целых чисел
            ids_list = [int(pk) for pk in ids.split(',')]
            # Удаляем всех стилей, чьи id попали в этот список
            Style.objects.filter(id__in=ids_list).delete()
            # Возвращаем 204 No Content — стандартный ответ успешного удаления
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
        

class SketchViewSet(viewsets.ModelViewSet):
    """Представление для работы с эскизами (набросками).

    Поддерживает все CRUD-операции, включая массовое создание,
    обновление и удаление. Действуют кастомные права доступа `SketchPermission`.
    GET-запросы на детальный просмотр кешируются на 15 минут.
    Фильтрация возможна по GET-параметрам `title` (подстрока) и `master_id` (точное совпадение).
    """

    # Указываем, что для преобразования объектов в JSON и обратно используется SketchSerializer
    serializer_class = SketchSerializer
    # Определяем базовый набор записей: все объекты модели Sketch
    queryset = Sketch.objects.all()
    # Подключаем кастомный класс ограничений прав доступа
    permission_classes = [SketchPermission]

    # Переопределяем метод, чтобы добавить фильтрацию и оптимизировать запросы к БД
    def get_queryset(self):
        # Вызываем родительский метод, сразу оптимизируя связи foreign key с помощью select_related,
        # чтобы избежать проблемы N+1 запросов при рендеринге вложенных сериализаторов мастеров и стилей.
        qs = super().get_queryset().select_related('master', 'style')
        # Берём параметры фильтрации из строки запроса
        title = self.request.query_params.get('title')
        master_id = self.request.query_params.get('master_id')
        
        # Если клиент передал название, фильтруем по подстроке без учета регистра
        if title:
            qs = qs.filter(title__icontains=title)
        # Если клиент передал ID мастера, фильтруем эскизы этого конкретного мастера
        if master_id:
            qs = qs.filter(master_id=master_id)
        # Возвращаем отфильтрованный и оптимизированный queryset
        return qs
    
    def list(self, request, *args, **kwargs):
        # Просто вызываем родительскую реализацию — она вернёт список набросков в JSON
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного наброска на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        # Родительский retrieve извлекает объект по id и отдаёт его данные
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового наброска (или нескольких)
    def create(self, request, *args, **kwargs):
        # Проверяем, является ли тело запроса списком (массовое создание) или одиночным объектом
        many = isinstance(request.data, list)
        # Создаём сериализатор: если many=True, то он ожидает список объектов
        serializer = self.get_serializer(data=request.data, many=many)
        # Запускаем валидацию, при ошибке автоматически вернётся ответ 400 с деталями
        serializer.is_valid(raise_exception=True)
        # Сохраняем новые объекты в базе
        self.perform_create(serializer)
        # Собираем заголовки ответа, например Location для созданного ресурса
        headers = self.get_success_headers(serializer.data)
        # Отдаём сериализованные данные с HTTP-статусом 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Полное обновление (PUT) одного или списка эскизов
    def update(self, request, *args, **kwargs):
        # Снова определяем, массовая операция или нет
        many = isinstance(request.data, list)
        if many:
            # Для списка из каждого элемента извлекаем id и находим соответствующий объект в базе
            instances = [Sketch.objects.get(pk=item['id']) for item in request.data]
            # Создаём сериализатор с найденными объектами и новыми данными, many=True
            serializer = self.get_serializer(instances, data=request.data, many=True)
        else:
            # Для одиночного объекта получаем его стандартным методом (по id из URL)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
        # Валидируем данные
        serializer.is_valid(raise_exception=True)
        # Сохраняем изменения
        self.perform_update(serializer)
        # Возвращаем обновлённые данные
        return Response(serializer.data)

    # Частичное обновление (PATCH) — работает как update, но с partial=True
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Sketch.objects.get(pk=item['id']) for item in request.data]
            # Обратите внимание: partial=True разрешает опускать обязательные поля
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких набросков
    def destroy(self, request, *args, **kwargs):
        # Проверяем, передан ли GET-параметр ids
        ids = request.query_params.get('ids')
        if ids:
            # Разбиваем строку с id (например, "1,2,3") на список целых чисел
            ids_list = [int(pk) for pk in ids.split(',')]
            # Удаляем всех набросков, чьи id попали в этот список
            Sketch.objects.filter(id__in=ids_list).delete()
            # Возвращаем 204 No Content — стандартный ответ успешного удаления
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)
        

class ClientViewSet(viewsets.ModelViewSet):
    """Представление для работы с клиентами студии.

    Поддерживает все CRUD-операции, включая массовое создание,
    обновление и удаление. GET-запросы на детальный просмотр кешируются на 15 минут.
    Фильтрация списка возможна по GET-параметру `name` (поиск по подстроке).
    """

    # Указываем, что для преобразования объектов в JSON и обратно используется ClientSerializer
    serializer_class = ClientSerializer
    # Определяем базовый набор записей: все объекты модели Client
    queryset = Client.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию по имени клиента
    def get_queryset(self):
        # Вызываем родительский метод, получая стандартный queryset
        qs = super().get_queryset()
        # Берём из параметров строки запроса значение по ключу 'name'
        name = self.request.query_params.get('name')
        # Если клиент передал имя, отбираем только тех клиентов, чьё имя содержит эту подстроку (без учёта регистра)
        if name:
            qs = qs.filter(name__icontains=name)
        # Возвращаем отфильтрованный (или исходный) queryset
        return qs
    
    def list(self, request, *args, **kwargs):
        # Просто вызываем родительскую реализацию — она вернёт список клиентов в JSON
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одного клиента на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        # Родительский retrieve извлекает объект по id и отдаёт его данные
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание нового клиента (или нескольких)
    def create(self, request, *args, **kwargs):
        # Проверяем, является ли тело запроса списком (массовое создание) или одиночным объектом
        many = isinstance(request.data, list)
        # Создаём сериализатор: если many=True, то он ожидает список объектов
        serializer = self.get_serializer(data=request.data, many=many)
        # Запускаем валидацию, при ошибке автоматически вернётся ответ 400 с деталями
        serializer.is_valid(raise_exception=True)
        # Сохраняем новые объекты в базе
        self.perform_create(serializer)
        # Собираем заголовки ответа, например Location для созданного ресурса
        headers = self.get_success_headers(serializer.data)
        # Отдаём сериализованные данные с HTTP-статусом 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Полное обновление (PUT) одного или списка клиентов
    def update(self, request, *args, **kwargs):
        # Снова определяем, массовая операция или нет
        many = isinstance(request.data, list)
        if many:
            # Для списка из каждого элемента извлекаем id и находим соответствующий объект в базе
            instances = [Client.objects.get(pk=item['id']) for item in request.data]
            # Создаём сериализатор с найденными объектами и новыми данными, many=True
            serializer = self.get_serializer(instances, data=request.data, many=True)
        else:
            # Для одиночного объекта получаем его стандартным методом (по id из URL)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
        # Валидируем данные
        serializer.is_valid(raise_exception=True)
        # Сохраняем изменения
        self.perform_update(serializer)
        # Возвращаем обновлённые данные
        return Response(serializer.data)

    # Частичное обновление (PATCH) — работает как update, но с partial=True
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Client.objects.get(pk=item['id']) for item in request.data]
            # Обратите внимание: partial=True разрешает опускать обязательные поля
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких клиентов
    def destroy(self, request, *args, **kwargs):
        # Проверяем, передан ли GET-параметр ids
        ids = request.query_params.get('ids')
        if ids:
            # Разбиваем строку с id (например, "1,2,3") на список целых чисел
            ids_list = [int(pk) for pk in ids.split(',')]
            # Удаляем всех клиентов, чьи id попали в этот список
            Client.objects.filter(id__in=ids_list).delete()
            # Возвращаем 204 No Content — стандартный ответ успешного удаления
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)
        

class SessionViewSet(viewsets.ModelViewSet):
    """Представление для работы с сессиями (сеансами татуировок).

    Поддерживает все CRUD-операции, включая массовое создание,
    обновление и удаление. GET-запросы на детальный просмотр кешируются на 15 минут.
    Позволяет фильтровать список сессий по `master_id`, `client_id` и `sketch_id`.
    """

    # Указываем, что для преобразования объектов в JSON и обратно используется SessionSerializer
    serializer_class = SessionSerializer
    # Определяем базовый набор записей: все объекты модели Session
    queryset = Session.objects.all()

    # Переопределяем метод, чтобы добавить фильтрацию и оптимизировать «тяжелые» SQL-запросы связи
    def get_queryset(self):
        # Применяем select_related для связей первого уровня (client, master, sketch) 
        # и двойное подчеркивание для связей внутри эскиза (sketch__master, sketch__style).
        # Это предотвращает лавинообразные запросы (проблема N+1) при генерации сложного JSON-ответа.
        qs = super().get_queryset().select_related(
            'client', 'master', 'sketch', 'sketch__master', 'sketch__style'
        )
        # Извлекаем параметры фильтрации из query string URL
        master_id = self.request.query_params.get('master_id')
        client_id = self.request.query_params.get('client_id')
        sketch_id = self.request.query_params.get('sketch_id')
        
        # Фильтруем сессии по мастеру, если передан параметр
        if master_id:
            qs = qs.filter(master_id=master_id)
        # Фильтруем сессии по конкретному клиенту
        if client_id:
            qs = qs.filter(client_id=client_id)
        # Фильтруем сессии по выбранному эскизу
        if sketch_id:
            qs = qs.filter(sketch_id=sketch_id)
        # Возвращаем отфильтрованный и оптимизированный по SQL-запросам набор сессий
        return qs
    
    def list(self, request, *args, **kwargs):
        # Просто вызываем родительскую реализацию — она вернёт список сессий в JSON
        return super().list(request, *args, **kwargs)
    
    # кешируем детальный просмотр одной сессии на 15 минут
    @cache_response(60 * 15)
    def retrieve(self, request, *args, **kwargs):
        # Родительский retrieve извлекает объект по id и отдаёт его данные
        return super().retrieve(request, *args, **kwargs)
    
    # Обработчик POST-запросов — создание новой сессии (или нескольких)
    def create(self, request, *args, **kwargs):
        # Проверяем, является ли тело запроса списком (массовое создание) или одиночным объектом
        many = isinstance(request.data, list)
        # Создаём сериализатор: если many=True, то он ожидает список объектов
        serializer = self.get_serializer(data=request.data, many=many)
        # Запускаем валидацию, при ошибке автоматически вернётся ответ 400 с деталями
        serializer.is_valid(raise_exception=True)
        # Сохраняем новые объекты в базе
        self.perform_create(serializer)
        # Собираем заголовки ответа, например Location для созданного ресурса
        headers = self.get_success_headers(serializer.data)
        # Отдаём сериализованные данные с HTTP-статусом 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # Полное обновление (PUT) одного или списка сессий
    def update(self, request, *args, **kwargs):
        # Снова определяем, массовая операция или нет
        many = isinstance(request.data, list)
        if many:
            # Для списка из каждого элемента извлекаем id и находим соответствующий объект в базе
            instances = [Session.objects.get(pk=item['id']) for item in request.data]
            # Создаём сериализатор с найденными объектами и новыми данными, many=True
            serializer = self.get_serializer(instances, data=request.data, many=True)
        else:
            # Для одиночного объекта получаем его стандартным методом (по id из URL)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
        # Валидируем данные
        serializer.is_valid(raise_exception=True)
        # Сохраняем изменения
        self.perform_update(serializer)
        # Возвращаем обновлённые данные
        return Response(serializer.data)

    # Частичное обновление (PATCH) — работает как update, но с partial=True
    def partial_update(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        if many:
            instances = [Session.objects.get(pk=item['id']) for item in request.data]
            # Обратите внимание: partial=True разрешает опускать обязательные поля
            serializer = self.get_serializer(instances, data=request.data, partial=True, many=True)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # Удаление (DELETE) — одного или нескольких сессий
    def destroy(self, request, *args, **kwargs):
        # Проверяем, передан ли GET-параметр ids
        ids = request.query_params.get('ids')
        if ids:
            # Разбиваем строку с id (например, "1,2,3") на список целых чисел
            ids_list = [int(pk) for pk in ids.split(',')]
            # Удаляем всех сессий, чьи id попали в этот список
            Session.objects.filter(id__in=ids_list).delete()
            # Возвращаем 204 No Content — стандартный ответ успешного удаления
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)