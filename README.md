# Проект парсинга pep

Парсер официальной документации python

```
positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

options:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```

Режимы работы:

- `whats-new` - собирает ссылки на статьи со страницы https://docs.python.org/3/whatsnew/.
Выводит на консоль или сохраняет в файл (в директорию `results`)
в зависимости от аргумента запуска `output`.

- `latest-versions` - собирает ссылки на страницы документации разных версий питона
со страницы https://docs.python.org/3/.
Выводит на консоль или сохраняет в файл (в директорию `results`)
в зависимости от аргумента запуска `output`.

- `download` - сохраняет архив документации с сайта в директорию `downloads` (pdf-версию)

- `pep` - собирает определённую статистику (сколько документов pep на сайте к какому типу относятся),
и сохраняет результат в csv-файл `results/results.csv`

Логирование настроено на ротацию в файл `logs/parser.log`
