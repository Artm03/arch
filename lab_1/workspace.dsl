workspace {
    name "Online Shop"
    description "Онлайн магазин"

    model {
        customer = person "Customer" "Покупатель"
        admin = person "Admin" "Администратор, управляет каталогом товаров"

        paymentSystem = softwareSystem "Payment System" "Внешняя платежная система" "External System"

        shopSystem = softwareSystem "Online Shop System" "Система онлайн-магазина для покупки товаров" {
            webApplication = container "Web Application" "Предоставляет пользовательский интерфейс" "React" "Web Browser" {
                uiComponent = component "UI Components" "React компоненты интерфейса" "React"
                webSocketClient = component "WebSocket Client" "Клиент для получения реал-тайм обновлений" "JavaScript/WebSocket"
            }

            apiGateway = container "API Gateway" "Маршрутизирует запросы к микросервисам" "Nginx, Traefik" "API Gateway" {
                httpProxy = component "HTTP Proxy" "Обрабатывает HTTP запросы" "Nginx/Traefik"
                webSocketProxy = component "WebSocket Proxy" "Обрабатывает WebSocket соединения" "Nginx/Traefik"

                userApiEndpoints = component "User API Endpoints" "1. POST /api/users - Создание нового пользователя\n2. GET /api/users?login={login} - Поиск пользователя по логину\n3. GET /api/users?name={name}&surname={surname} - Поиск пользователя по маске имя и фамилии" "API Endpoints"
                productApiEndpoints = component "Product API Endpoints" "1. POST /api/products - Создание товара\n2. GET /api/products - Получение списка товаров" "API Endpoints"
                cartApiEndpoints = component "Cart API Endpoints" "1. POST /api/cart/items - Добавление товара в корзину\n2. GET /api/users/{userId}/cart - Получение корзины для пользователя" "API Endpoints"
            }

            notificationService = container "Notification Service" "Отправляет уведомления в реальном времени" "Python, FastAPI" "Microservice" {
                notificationAPI = component "Notification API" "API для управления уведомлениями" "FastAPI"
                webSocketHandler = component "WebSocket Handler" "Обрабатывает WebSocket соединения" "FastAPI WebSockets"
                notificationConsumer = component "Notification Consumer" "Получает события из Kafka для отправки уведомлений" "Kafka Consumer"
            }

            userService = container "User Service" "Управление пользователями" "Python, FastAPI" "Microservice" {
                userAPI = component "User API" "API для управления пользователями" "FastAPI"
                userPublisher = component "User Event Publisher" "Публикует события пользователей в Kafka" "Kafka Producer"
    
                createUserEndpoint = component "Create User" "POST /api/users - Создание нового пользователя" "FastAPI Endpoint"
                findUserByLoginEndpoint = component "Find User by Login" "GET /api/users?login={login} - Поиск пользователя по логину" "FastAPI Endpoint"
                findUserByNameEndpoint = component "Find User by Name" "GET /api/users?name={name}&surname={surname} - Поиск пользователя по маске имя и фамилии" "FastAPI Endpoint"

                userPublisherGoals = component "User Event Publishing Goals" "Цели: 1) Уведомление других сервисов об изменениях в данных пользователей\n2) Обеспечение отслеживаемости действий пользователей\n3) Поддержание актуальных данных в других сервисах" "Documentation"
            }

            productService = container "Product Service" "Управление каталогом товаров" "Python, FastAPI" "Microservice" {
                productAPI = component "Product API" "API для управления товарами" "FastAPI"
                productPublisher = component "Product Event Publisher" "Публикует события товаров в Kafka" "Kafka Producer"
                productConsumer = component "Product Event Consumer" "Обрабатывает связанные с товарами события" "Kafka Consumer"
    
                createProductEndpoint = component "Create Product" "POST /api/products - Создание товара" "FastAPI Endpoint"
                getProductsEndpoint = component "Get Products" "GET /api/products - Получение списка товаров" "FastAPI Endpoint"

                productKafkaGoals = component "Product Kafka Goals" "Цели: 1) Информирование о изменениях в каталоге\n2) Обеспечение актуальности цен и наличия товаров\n3) Синхронизация данных между сервисами\n4) Обновление статистики на основе заказов" "Documentation"
            }

            cartService = container "Cart Service" "Управление корзиной пользователя" "Python, FastAPI" "Microservice" {
                cartAPI = component "Cart API" "API для управления корзиной" "FastAPI"
                cartPublisher = component "Cart Event Publisher" "Публикует события корзины в Kafka" "Kafka Producer"
                cartConsumer = component "Cart Event Consumer" "Обрабатывает связанные с корзиной события" "Kafka Consumer"
    
                addToCartEndpoint = component "Add To Cart" "POST /api/cart/items - Добавление товара в корзину" "FastAPI Endpoint"
                getUserCartEndpoint = component "Get User Cart" "GET /api/users/cart - Получение корзины для пользователя" "FastAPI Endpoint"

                cartKafkaGoals = component "Cart Kafka Goals" "Цели: 1) Уведомление Order Service о начале оформления заказа\n2) Синхронизация с актуальными данными о товарах\n3) Согласованность данных между корзиной и профилем пользователя\n4) Реагирование на изменения товаров и пользователей" "Documentation"
            }

            orderService = container "Order Service" "Обработка заказов" "Python, FastAPI" "Microservice" {
                orderAPI = component "Order API" "API для управления заказами" "FastAPI"
                orderPublisher = component "Order Event Publisher" "Публикует события заказов в Kafka" "Kafka Producer"
                orderConsumer = component "Order Event Consumer" "Обрабатывает связанные с заказами события" "Kafka Consumer"

                orderKafkaGoals = component "Order Kafka Goals" "Цели: 1) Отслеживание и управление жизненным циклом заказа\n2) Координация процесса платежа\n3) Уведомление о статусах заказа и платежа\n4) Обеспечение целостности данных заказа\n5) Реагирование на изменения в корзинах" "Documentation"
            }

            orderHistoryService = container "Order History Service" "Отслеживание истории статусов заказов" "Python, FastAPI" "Microservice" {
                historyAPI = component "History API" "API для доступа к истории заказов" "FastAPI"
                historyPublisher = component "History Event Publisher" "Публикует события истории в Kafka" "Kafka Producer"
                historyConsumer = component "History Event Consumer" "Обрабатывает события статусов заказов" "Kafka Consumer"

                historyKafkaGoals = component "History Kafka Goals" "Цели: 1) Построение полной хронологии изменений статусов\n2) Создание аудиторского следа для всех операций\n3) Обеспечение возможности анализа и отчетности\n4) Предоставление данных для разрешения споров" "Documentation"
            }

            userDb = container "User Database" "Данные пользователей" "PostgreSQL" "Database"
            productDb = container "Product Database" "Каталог товаров" "PostgreSQL" "Database"
            cartDb = container "Cart Database" "Корзины пользователей" "PostgreSQL" "Database"
            orderDb = container "Order Database" "Заказы" "PostgreSQL" "Database"
            orderHistoryDb = container "Order History Database" "История статусов заказов" "PostgreSQL" "Database"

            messageBus = container "Message Bus" "Асинхронная коммуникация между сервисами" "Kafka" "Message Bus" {
                userTopic = component "User Events Topic" "Хранит события пользователей" "Kafka Topic"
                productTopic = component "Product Events Topic" "Хранит события товаров" "Kafka Topic"
                cartTopic = component "Cart Events Topic" "Хранит события корзины" "Kafka Topic"
                orderTopic = component "Order Events Topic" "Хранит события заказов" "Kafka Topic"
                historyTopic = component "History Events Topic" "Хранит события истории заказов" "Kafka Topic"
                notificationTopic = component "Notification Events Topic" "Хранит события для уведомлений" "Kafka Topic"

                kafkaGoals = component "Kafka Benefits" "Преимущества: 1) Отделение производителей от потребителей\n2) Масштабируемость\n3) Надежность и гарантия доставки\n4) Сохранение порядка сообщений\n5) Возможность повторной обработки\n6) Снижение связанности" "Documentation"
            }

            userApiEndpoints -> createUserEndpoint "Создание пользователя" "JSON/HTTPS"
            userApiEndpoints -> findUserByLoginEndpoint "Поиск по логину" "JSON/HTTPS"
            userApiEndpoints -> findUserByNameEndpoint "Поиск по имени/фамилии" "JSON/HTTPS"

            productApiEndpoints -> createProductEndpoint "Создание товара" "JSON/HTTPS"
            productApiEndpoints -> getProductsEndpoint "Получение товаров" "JSON/HTTPS"

            cartApiEndpoints -> addToCartEndpoint "Добавление в корзину" "JSON/HTTPS"
            cartApiEndpoints -> getUserCartEndpoint "Получение корзины" "JSON/HTTPS"

            webApplication -> apiGateway "Отправляет запросы" "JSON/HTTPS"
            webSocketClient -> webSocketProxy "Подключается для получения уведомлений" "WebSocket"

            messageBus -> notificationService "Отправляет события для уведомлений" "Kafka Protocol"

            webSocketHandler -> webSocketProxy "Отправляет уведомления" "WebSocket"
            webSocketProxy -> webSocketClient "Передает уведомления" "WebSocket"

            apiGateway -> userService "Запросы пользователей" "JSON/HTTPS"
            apiGateway -> productService "Запросы товаров" "JSON/HTTPS"
            apiGateway -> cartService "Запросы корзины" "JSON/HTTPS"
            apiGateway -> orderService "Запросы заказов" "JSON/HTTPS"
            apiGateway -> orderHistoryService "Запросы истории заказов" "JSON/HTTPS"
            apiGateway -> notificationService "Запросы уведомлений" "JSON/HTTPS"

            userService -> userDb "CRUD операции" "SQLAlchemy/PostgreSQL"
            productService -> productDb "CRUD операции" "SQLAlchemy/PostgreSQL"
            cartService -> cartDb "CRUD операции" "SQLAlchemy/PostgreSQL"
            orderService -> orderDb "CRUD операции" "SQLAlchemy/PostgreSQL"
            orderHistoryService -> orderHistoryDb "CRUD операции" "SQLAlchemy/PostgreSQL"

            userPublisher -> messageBus "Публикует события" "Kafka Protocol"

            productPublisher -> messageBus "Публикует события" "Kafka Protocol"
            productConsumer -> messageBus "Подписывается на события" "Kafka Protocol"

            cartPublisher -> messageBus "Публикует события" "Kafka Protocol"
            cartConsumer -> messageBus "Подписывается на события" "Kafka Protocol"

            orderPublisher -> messageBus "Публикует события" "Kafka Protocol"
            orderConsumer -> messageBus "Подписывается на события" "Kafka Protocol"

            historyPublisher -> messageBus "Публикует события" "Kafka Protocol"
            historyConsumer -> messageBus "Подписывается на события статусов заказов" "Kafka Protocol"

            notificationConsumer -> messageBus "Подписывается на события для уведомлений" "Kafka Protocol"

            userPublisher -> userTopic "Публикует события: user.created, user.updated, user.deleted, user.login" "Kafka Protocol"

            productPublisher -> productTopic "Публикует события: product.created, product.updated, product.price_changed" "Kafka Protocol"
            productConsumer -> orderTopic "Подписывается на: order.created, order.completed" "Kafka Protocol"

            cartPublisher -> cartTopic "Публикует события: cart.item_added, cart.updated, cart.checkout_started" "Kafka Protocol"
            cartConsumer -> userTopic "Подписывается на: user.created, user.deleted" "Kafka Protocol"
            cartConsumer -> productTopic "Подписывается на: product.updated, product.out_of_stock" "Kafka Protocol"

            orderPublisher -> orderTopic "Публикует события: order.created, order.status_changed, order.payment_initiated" "Kafka Protocol"
            orderConsumer -> cartTopic "Подписывается на: cart.checkout_started" "Kafka Protocol"
            orderConsumer -> productTopic "Подписывается на: product.price_changed, product.out_of_stock" "Kafka Protocol"

            historyPublisher -> historyTopic "Публикует события: order_history.recorded, order_history.report_generated" "Kafka Protocol"
            historyConsumer -> orderTopic "Подписывается на: order.created, order.status_changed, order.canceled" "Kafka Protocol"

            notificationConsumer -> orderTopic "Подписывается на события заказов для уведомлений" "Kafka Protocol"
            notificationConsumer -> userTopic "Подписывается на события пользователей для уведомлений" "Kafka Protocol"
            notificationConsumer -> productTopic "Подписывается на события товаров для уведомлений" "Kafka Protocol"
            notificationConsumer -> historyTopic "Подписывается на события истории для уведомлений" "Kafka Protocol"

            cartService -> userService "Проверяет пользователя" "JSON/HTTPS"
            cartService -> productService "Проверяет товары" "JSON/HTTPS"
            orderService -> cartService "Получает корзину" "JSON/HTTPS"
            orderService -> userService "Проверяет пользователя" "JSON/HTTPS"
            orderHistoryService -> orderService "Запрашивает детали заказа" "JSON/HTTPS"

            orderService -> paymentSystem "Обрабатывает платежи" "JSON/HTTPS"
        }

        customer -> shopSystem "Использует для покупок"
        admin -> shopSystem "Управляет системой"

        customer -> webApplication "Просматривает и покупает"
        admin -> webApplication "Управляет"
    }

    views {
        systemContext shopSystem "SystemContext" {
            include *
            autoLayout
        }

        container shopSystem "Containers" {
            include *
            autoLayout
        }

        component apiGateway "APIEndpoints" {
            include *
            autoLayout
        }

        component userService "UserServiceComponents" {
            include *
            autoLayout
        }

        component productService "ProductServiceComponents" {
            include *
            autoLayout
        }

        component cartService "CartServiceComponents" {
            include *
            autoLayout
        }

        component orderService "OrderServiceComponents" {
            include *
            autoLayout
        }

        component orderHistoryService "OrderHistoryServiceComponents" {
            include *
            autoLayout
        }

        component notificationService "NotificationServiceComponents" {
            include *
            autoLayout
        }

        component messageBus "KafkaComponents" {
            include *
            autoLayout
        }

        dynamic shopSystem "GetUserCart" "Получение корзины для пользователя" {
            customer -> webApplication "Открывает корзину"
            webApplication -> apiGateway "GET /api/users/cart"
            apiGateway -> cartService "Перенаправляет запрос"
            cartService -> cartDb "Получает данные корзины"
            cartDb -> cartService "Возвращает данные"
            cartService -> productService "Получает актуальные данные о товарах"
            productService -> cartService "Возвращает данные товаров"
            cartService -> apiGateway "Возвращает корзину с товарами"
            apiGateway -> webApplication "Передает данные корзины"
            webApplication -> customer "Отображает корзину с товарами"
            autoLayout
        }

        dynamic shopSystem "OrderStatusChange" "Изменение статуса заказа и логирование истории" {
            admin -> webApplication "Изменяет статус"
            webApplication -> apiGateway "PUT /api/orders/status"
            apiGateway -> orderService "Перенаправляет запрос"
            orderService -> orderDb "Обновляет статус"
            orderDb -> orderService "Подтверждает"
            orderService -> messageBus "Публикует событие order.status_changed"
            messageBus -> orderHistoryService "Передает событие"
            orderHistoryService -> orderService "Запрашивает детали"
            orderService -> orderHistoryService "Возвращает детали"
            orderHistoryService -> orderHistoryDb "Сохраняет в историю"
            orderHistoryService -> messageBus "Публикует order_history.recorded"
            orderService -> apiGateway "Возвращает заказ"
            apiGateway -> webApplication "Возвращает успешный ответ"
            webApplication -> admin "Обновляет UI"
            autoLayout
        }

        theme default
    }
}
