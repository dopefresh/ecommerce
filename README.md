### Для оплаты используйте инструкцию https://yookassa.ru/developers/using-api/testing#test-bank-card-success

website: https://ecommerce-by-popov-vasilii-app.ru.com/
gmail: dopefresh4000@gmail.com

# Коротко о проекте:
ecommerce магазин с товарами, спарсенными с dns-shop.ru, к сожалению когда парсил забыл про картинки, 
Функционал:
1. Просмотр товаров, категории, подкатегории
2. Добавление товаров в корзину, удаление и изменение их количества в ней
3. Оплата с помощью ЮКассы(тестовая, тк реального продукта я не произвожу и ничего вам не высылаю)
4. Как только оплатите статус заказа поменяется и ваша корзина очистится
5. Мультиязычность(английский/русский), не полная, названия товаров на русском
6. Заказ в дальнейшем должен менять свой статус каждые 20 секунд, но пока не нашёл в документации из за чего ошибка

## Использованные технологии:
1. Django
2. Django-allauth(с Google Oauth Provider)
3. Django translation framework
4. Yookassa(вебхуком мне приходит уведомление об оплате)
5. PostgreSQL
6. PgBouncer для управления и оптимизации соединений к бд
7. Nginx(letsencrypt с помощью certbot) использовал сайт https://www.digitalocean.com/community/tools/nginx + небольшие доработки
8. Gunicorn
9. Celery(RabbitMQ как брокер сообщений + Redis как результирующий бэкенд)
10. Bootstrap
11. AJAX(axios) + CORS(django cors headers)

В верхнем правом углу есть кнопки смены языка, до конца я не довёл перевод
(описания и названия товаров только на русском), так как у меня нет на это времени в данный момент

Сервер с одним ядром и с 1гб оперативы на reg.ru.
Nginx, Gunicorn, PostgreSQL, Celery Worker делят 1 ядро, поэтому сайт может сильно тормозить,
так как это пет проект, то сильно затрачиваться на сервер я не собираюсь, поэтому не судите строго. 
Пожалуйста сообщите если этот проект действительно не дотягивает на уровень джуна, так как
мой счёт на облачных серверах через ~2 месяца дойдёт до нуля. 
Вёрстка действительно проста и ужасна, так как я не желаю быть фронтэндером на каком либо проекте
и не имею тут никаких особых умений, также очень буду рад роли DBA и девопс и имею огромное желание попробовать кластеризацию бд,
а также микросервисы(скорее всего ими я и займусь в свободное время).
