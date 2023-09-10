# Сайт [*MusicAnalisys*](http://anesthesia.pythonanywhere.com/)
Индивидуальный итоговый проект по предмету *Программирование и лингвистические данные*. Выполнила Добрынина Анастсаия, ВШЭ, Фундаментальная и компьютерная лингвистика, 2023

Сайт реализован в меньшем функционале, чем планировался изначально в силу ограниченного хранилища на платформе pythonanywhere. В репозитории лежит изначальных код, а код на pythonanywhere несколько отличается, обладает меньшим функционалом.

Сайт получает запрос в виде названия исполнителя и собирает тексты песен этого исполнителя с ресруса [Амальгама](https://www.amalgama-lab.com/). Амальгама была выбрана из-за четкой структуры сайта: всех имеющихся музыкантов можно найти по первой букве и получить доступ ко всем песням в одной вкладке. Такой удобной структуры нет у других известных мне сайтов с тектсами песен (например, [Genius lyrics](https://genius.com/), [lyrsense.com](https://lyrsense.com/)). Краулер для Амальгамы написан: он не учитывает разницу в заглавных/строчных буквах и приспособлен к одной из особенностей сайта (если название группы начинается на *the*, артикль переносится в конец: *Beatles, the*). Код краулера есть в коде проекта: это функции `find_one_band` и `find_lyric` в документе `functions.py`. Он использовался при сборе базы данных, но на действующем сайте краулер не применяется

Затем тексты лемматизировались при помощи модуля `stanza` - удобный и многофункциональный модуль для анализа английского языка. С помощью функции `lemmatize` исходный текст приводился к нижнему регистру, избавлялся от знаков препинания, стоп слов, лемматизированлся, а также функция возвращала количество слов определенных частей речи.

Затем все эти данные записывались в базу. Устройство базы: 

* есть таблица с названиями групп, где каждой присваивался уникальный id. Здесь также хранится информация о количестве разных частей речи, посокльку иначе неудобно было бы выводиьт данные групп, которые уже есть в базе (пришлось бы еще раз обрабатывать тектсы) Колонки: `id` - ключ, `band_name`, и частиречные: `verbs`, `nouns`, `adjectives`, `adverbs`, `propernouns`

* вторая таблица с текстами песен: каждой песне присвоен id, но также у каждой помечен исполнитель с помощью его id. Колонки: `song_id`, `song_name`, `band_id` - связанная с предыдущей таблицей, `text`- леммы

Если же название исполнителя не новое, а уже лежит в базе, программа не искала его на сайте и обрабатывала, а сразу брала данные из базы.

**Модуль `stanza` занимал более 50% памяти на платформе pythonanywhere, поэтому часть с обработкой новых полученных исполнителей пришлось убрать**

Зато теперь сайт обладает большой базой данных, состоящей из более чем 30 исполнителей. Пользователь может выбрать любого из них, посмотеть анализ его песен и увидеть анализ всех имеющихся исполнителей на общей диаграмме - этот функционал остался неизменным. Рассмотрим его подробнее

На странице "Поиск" можно ввести название исполнителя и увидеть следующие данные:

* первый абзац из википедии - чтобы напомнить пользователю общую информацию об исполнители (берется автоматически при помощи модуля `Wikipedia`)

* объем корпуса данного исполнителя

* количество лемм - это важный показатель, так как отражает "словарный запас" музыканта 

* график семантической близости - сделан путем преобразования tf-idf песен с помощью PCA, выведен при помощи Javascript Charts.js. Здесь интересно наблюдать, как в творчестве музыкантов кластерезуются или не кластерезуются песни с одних альбомов, на одну тематику

* также с помощью tf-idf выводятся ключевые слова во всем творчестве исполнителя

* с ними интересно сравнить просто самые частые слова, подсчитанные при помощи Counter. Если ключевые слова - самые важные по смыслу, то это просто самые повторяемые - и эти показатели часто сильно отличаются

* наконец, выводится распределение по частям речи. Были взяты только глаголы, существительные, наречия, прилагательные и имена собственные, так как это больше всего говорит о творчестве исполнителя. Тем более, многие местоимения, частицы и тп. были убраны из текстов на этапе лемматизации. Имена собственные выделяются в отдельную категорию, так как это тоже важный для анализа творчества исполнителя показатель - например, в творчестве My Chemical Romance важную роль играет название штата - LA

Во вкладке "Все группы" представлена диаграмма аналогична диаграмме по песням одной группы: на ней результаты обработки текстов всех групп с помощью tf-idf и преобразованные в график с помощью метода PCA. Таким образом мы можем видеть, насколько одни исполнители похожи на других. Можно видеть некоторую кластеризацию исполнителей поп-музыки, рока, металла



