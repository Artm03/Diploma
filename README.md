# Выпускная квалификационная работа

## Онлайн-сервис создания фотогалерей с применением нейросетевых технологий распознавания лиц

**Студент**: А. А. Гаврилов

**Группа**: М8О-406Б-20

**Научный руководитель**: Л. Н. Чернышов

## Цель и задачи работы

**Цель** - обеспечить пользователей средством для работы с фотогалереями с возможностью идентификации отдельных личностей на фотографиях.

**Задачи**:

- реализовать работу технологии идентификации лиц;
- разработать архитектуру серверного и клиентского приложений;
- реализовать систему авторизации и аутентификации;
- реализовать систему фотогалерей.

## Задачи на разработку

-	выбрать, добавить и протестировать нейронную сеть для идентификации лиц, продумать способ хранения векторов, которые запоминаются в процессе запоминания лица;
-	продумать схему БД, в которой будут храниться все пользователи, их email-коды и сессии, каким образом будет происходить взаимодействие сервера с клиентом. Реализовать регистрацию/авторизацию и аутентификацию пользователя, сделать их двухфакторными, для этого подключить почтовый клиент, чтобы отправлять на почту пользователя код;
-	продумать схему БД, в которой будут храниться галереи, информация о них, каким образом к ним будут привязаны изображения, а также каким образом будет храниться список имён личностей, которые были сохранены пользователем или идентифицированы нейронной сетью;
-	реализовать систему, в которой будет корректное взаимодействие всех составных частей, описанных выше, также продумать каким образом пользователь будет взаимодействовать с этой системой и реализовать это взаимодействие.

**В текущем репозитории представлен код серверной части приложения.**
