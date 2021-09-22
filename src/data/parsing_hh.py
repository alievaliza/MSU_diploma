# PART 0 Получаем id регионов
req = requests.get('https://api.hh.ru/areas')  # Посылаем запрос к API
data = req.content.decode()  # Декодируем его ответ, чтобы Кириллица отображалась корректно
req.close()
# Преобразуем полученный текст в объект справочника
jsonObj = json.loads(data)
areas_id, countries_name = [], []
for i in range(len(jsonObj)):
    for area in jsonObj[i]['areas']:
        areas_id.append(area)
        countries_name.append(jsonObj[i]['name'])
df_areas = pd.DataFrame(areas_id)
df_areas['country_name'] = countries_name
# df_areas.to_excel('areas.xlsx', index=False)



# PART 1
# Зададим время ожидания, равное 70 минутам, установленное эмпирически
wait = 4200
print("Введите from_area от 0 до 647 включительно (0 если сборка первая, 647 если сборка не нужна):")
try:
    from_area = int(input())
except:
    from_area = 0
getAllPages(df_areas, wait, from_area)
print('\nСтраницы поиска собраны')

# PART 2
getAllVacancies(wait)
print('\nВакансии собраны')

# PART 3 (released in Colab)

# Часть для Google Colab. Загрузка файла 'vacancies.zip' с гугл-драйва и его распаковка
# url = '1vGZg5w7mFYwxRzE96xZuxn_Lv_uq_soy'
# output = "vacancies.zip"
# gdown.download('https://drive.google.com/uc?export=download&id=' + url, output, quiet=False)
# zf = zipfile.ZipFile("vacancies.zip")
# zf.extractall()

try:
    df = makeDataframe()
except:
    print("Нехватка оперативной памяти. Попробуйте реализовать в Google Colab")
    quit()

try:
    df.to_excel('vacancies.xlsx', index=False)
except:
    print("Нехватка оперативной памяти. Попробуйте разбить df на 2 или более частей")
    quit()
# Выводим сообщение об окончании программы
display.clear_output(wait=True)
display.display('Вакансии загружены в файл')