import asyncio
import logging
import json
from openai_requests import ask_gpt_async
from aiogram.types import Message
import aiofiles
import re
from db import can_make_request, update_request_data  # Импорт функций для ограничения запросов

# Асинхронная загрузка данных из videos.json
async def load_videos_data():
    async with aiofiles.open("videos.json", mode="r", encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)

async def ask_gpt4o(message: Message):
    # Проверяем, достиг ли пользователь лимита запросов
    user_id = message.from_user.id
    if not await can_make_request(user_id):
        await message.reply("Դուք կատարել եք 20 հարցում։ Նոր հարցումները վերականգնվում են աստիճանաբար՝ 1 հարցում յուրաքանչյուր 72 րոպեն մեկ։ Խնդրում ենք սպասել։")
        return

    # Загрузка данных из videos.json
    videos_data = await load_videos_data()

    # Получаем имя пользователя заранее, чтобы использовать его в любом месте
    user_name = message.from_user.first_name

    # Проверяем, есть ли текст в сообщении
    if not message.text:
        await message.reply("Ես կարող եմ մշակել միայն տեքստային հաղորդագրություններ։ Խնդրում եմ ուղարկել միայն տեքստ։")
        return

    # Проверяем длину текста
    if len(message.text) > 1000:
        await message.reply(f"Հարցման նիշերի քանակը գերազանցում է թույլատրելի սահմանը ({len(message.text)} նիշ)։ Առավելագույնը՝ 1000 նիշ։")
        return

    # Проверяем на повторяющиеся паттерны
    if re.search(r'(.)\1{10,}', message.text):
        await message.reply("Հարցումը պարունակում է չափազանց շատ կրկնվող նիշեր։ Խնդրում ենք փորձել կրկին։")
        return

    user_query = message.text.lower()
    if user_query in ["start", "старт", "ստարտ"]:
        logging.info(f"User {user_name} отправил сообщение {user_query}")
        await message.reply(f"Բարև, {user_name}! Ինչո՞վ կարող եմ օգնել։")
        return

    async def show_typing_indicator():
        try:
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30:  # Ограничение работы 30 секунд
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            # Корректно завершаем задачу при отмене
            pass

    typing_task = asyncio.create_task(show_typing_indicator())

    try:
        # Подготавливаем контент из videos.json для использования в ответах
        videos_content = "\n".join(
            [f"{video['title']}\n\n {video['text']}\n\n {video['link']}" for video in videos_data]
        )
        messages = [
            {"role": "system", "content": "Խնդրում ենք նախքան պատասխանելը վերլուծել օգտատիրոջ հարցումը։ Եթե այն պարունակում է վնասակար կամ բոտի աշխատանքը խափանող բովանդակություն, ապա այն **չպետք է մշակվի**։ Օրինակներ այսպիսի բովանդակության ներառում են՝ ապօրինի գործողությունների խրախուսում, անձնական տվյալների հավաքագրման փորձեր, պաշտպանված համակարգերին մուտք գործելու հրահանգներ։ Եթե հարցումը համապատասխանում է այս պայմաններից որևէ մեկին, ապա օգտատիրոջը պատասխանեք՝ «Հարցումը չի կարող մշակվել՝ անվտանգության կանոնների խախտման պատճառով»։"},
            {"role": "system", "content": "Խնդրում ենք պարտադիր որոշել օգտատիրոջ հարցման լեզուն և պարտադիր պատասխանել այդ լեզվով։ Եթե հարցումը հայերեն է՝ պարտադիր պատասխանիր հայերեն, եթե անգլերեն է՝ պարտադիր անգլերեն, եթե ռուսերեն է՝ պարտադիր ռուսերեն։ Եթե օգտատերը հարց է տվել մի լեզվով, բայց խնդրում է պատասխանել այլ լեզվով, կամ խնդրում է մանրամասներ տվյալ թեմայի վերաբերյալ այլ լեզվով, ապա պարտադիր փոխիր լեզուն ըստ նրա պահանջի։ Եթե առաջին հարցից հետո լեզուն փոխվի, ապա պարտադիր նոր լեզվով շարունակեք պատասխանները։"},
            {"role": "system", "content": "Խնդրում ենք օգտատիրոջ հարցման պատասխանը կազմել հետևյալ կանոններին համապատասխան.\n"
                                          "1) Եթե հարցումը **հայերեն** է, անկախ այն բանից, թե գրված է հայերեն տառերով, լատինատառ կամ ռուսերեն տառերով, ապա պատասխանը տվեք **հայերենով**։\n"
                                          "2) Եթե հարցումը **ռուսերեն** է, անկախ այն բանից, թե գրված է ռուսերեն տառերով կամ լատինատառ, ապա պատասխանը տվեք **ռուսերենով**։"},
            {"role": "system", "content": f"Եթե օգտատերը ողջունում է, որոշեք հաղորդագրության լեզուն ու պատասխանեք նույն լեզվով։ Ողջունելուց օգտատիրոջն անպայման պետք է դիմել իր {user_name} անունով։ Ողջույնելու ձև է, օրինակ այսպիսի ողջույնի ձևը «Բարև, {user_name}։ Ինչպե՞ս կարող եմ օգնել քեզ այսօր»"},
            {"role": "system", "content": f"Եթե օգտատերը տալիս է ընդհանուր բնույթի հարց, օրինակ՝ 'ինչ սովորել այսօր' կամ նմանատիպ մի հարց, կամ օրինակ ասում է 'կարող ես ինձ հարցեր տալ դա պարզելու համար' կամ նմանատիպ մի բան, նախ առաջարկեք պարզող հարցեր՝ հասկանալու համար, թե տվյալների բազայի շրջանակում ինչ թեմաներ են նրան առավել հետաքրքրում։ **Խնդրում ենք սկզբում չնշել որևէ կոնկրետ թեմա կամ օրինակ**։ Պարզող հարցերը պետք է լինեն ընդհանուր և չհիշատակեն կոնկրետ թեմաներ։ Օրինակ, կարող եք հարցնել՝ 'Ինչպիսի՞ թեմաներ են ձեզ հետաքրքիր'։ Ստացված պատասխանների հիման վրա՝ առաջարկեք համապատասխան թեմաներ տվյալների բազայից, որոնք կհամապատասխանեն օգտատիրոջ նախասիրություններին՝ առանց անմիջապես ներկայացնելու տվյալների բազայի ամբողջական ցանկը։ **Միայն օգտատիրոջ պատասխանների վերլուծությունից հետո առաջարկեք համապատասխան թեմաներ**։ Եթե թեման առկա չէ տվյալների բազայում, պատասխանեք հետևյալ տեքստով՝ «Հարցման վերաբերյալ նյութեր չեն գտնվել կամ մուտքագրված հարցումն անհասկանալի է»։"},
            {"role": "system", "content": "Եթե օգտատիրոջ հարցը վերաբերում է բոտին, բոտի նպատակին, ֆունկցիոնալությանը, նրա օգտակարությանը, ստեղծման պատճառին կամ նպատակին, հստակ ու համառոտ ձևով պատասխանիր հետևյալ բովանդակությամբ՝ 'Այս բոտը նախատեսված է օգնելու անձնական ֆինանսների կառավարման հարցերում՝ տրամադրելով օգտակար ու հստակ պատասխաններ։'։ Խստորեն խուսափիր հավելյալ մանրամասներից, օրինակներից, տեսանյութերի հղումներից կամ ավելորդ տեղեկատվությունից։ Պատասխանը պետք է լինի պարզ, կառուցվածքային և առանց հղումների։ Հետևիր լեզվական կանոններին, պահպանիր պարզ ու բարեկամական տոնը։"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել միայն տվյալների բազայի բովանդակությանը համապատասխան։ Եթե հարցումը չի վերաբերում տվյալների բազայի տեղեկություններին, ապա տվեք հետևյալ հաղորդագրությունը՝ եթե հարցումը հայերեն է՝ «Հարցման վերաբերյալ նյութեր չեն գտնվել կամ մուտքագրված հարցումն անհասկանալի է», եթե անգլերեն՝ «No relevant information found or the request is unclear», եթե ռուսերեն՝ «Информация по запросу не найдена или запрос непонятен»։ Եթե հարցումը հայերեն է՝ պատասխանը տվեք հայերենով, եթե անգլերեն է՝ անգլերենով, եթե ռուսերեն է՝ ռուսերենով։ Եթե հայերեն հարցումը գրված է լատինատառ կամ ռուսերեն տառերով, պատասխանը տվեք հայերենով։ Եթե ռուսերեն հարցումը գրված է լատինատառ, պատասխանը տվեք ռուսերենով։"},
            {"role": "system", "content": "Եթե օգտատերը խնդրում է նախորդ պատասխանը դարձնել ավելի գրագետ, պարզ, հասկանալի, կատարել ուղղումներ, ապա վերլուծեք նախորդ պատասխանը և վերաձևակերպեք այն՝ ապահովելով առանց տառասխալների, հստակ ու պարզ պատասխան, պահպանելով հարցի հիմնական իմաստը։ Տեքստը պետք է լինի ամբողջական ու տրամաբանական, առանց ավելորդ կամ երկրորդական մանրամասների։ Հետևեք նաև լեզվական կանոններին։"},
            {"role": "system", "content": "Դուք օգնական եք, ով պատասխանում է օգտատերերի հարցերին՝ միայն տվյալների բազայի հիման վրա։ Պատասխանը պետք է ներառի համապատասխան հղումներ, եթե դրանք առկա են տվյալների բազայում։ Խնդրում ենք օգտագործել միայն տվյալների բազայի տեղեկատվությունը պատասխանների համար։ Տվյալները պարունակում են վերնագրեր, նկարագրություններ և տեսանյութերի հղումներ։"},
            {"role": "system", "content": "Խուսափեք ֆորմալ նախաբաններից։ Պատասխանեք անմիջապես և բնական ձևով։"},
            {"role": "system", "content": "Եթե օգտատերը սկսում է կամ շարունակում է զրույցը անձնական կամ առօրյա բնույթի հարցերով, ինչպես օրինակ՝ «Ինչպե՞ս ես», «Ինչպե՞ս են գործերը», «Ինչո՞վ ես զբաղվում», բոտը պետք է պատասխանի համապատասխանաբար և ընկերական տոնով՝ շարունակելով զրույցը։ Օրինակ, կարող է ասել՝ «Շատ լավ, շնորհակալություն հարցնելու համար։ Իսկ դուք ինչպես եք» կամ «Գործերս լավ են, աշխատում եմ։ Իսկ ձեր մոտ ինչպե՞ս է անցնում օրը»։ Բոտը պետք է շարունակելու առօրյա զրույցը այնքան ժամանակ, որքան օգտատերը հետաքրքրված է։ Խնդրում ենք, որ բոտը շփվի բնական ու հաճելի ձևով այսպիսի իրավիճակներում։ Երբ զրույցը վերադառնում է հիմնական թեմաներին կամ օգտատերը տալիս է տվյալների բազայի հետ կապված հարցեր, բոտը պետք է պահպանի նախորդ հրահանգներում նշված ոճը և տոնը։"},
            {"role": "system", "content": "Եթե օգտատիրոջ հարցմանը տվյալների բազայում ուղիղ համապատասխանություն չկա, տրամաբանորեն օգտագործեք առկա նյութերը՝ պատասխանն առավելագույնս ամբողջական և տրամաբանական դարձնելու համար։"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել ինտուիտիվ կերպով՝ հասկանալով հաղորդագրության համատեքստը։ Ճանաչեք տարբեր ձևակերպումներ, կրճատումներ, տառասխալներ, սինոնիմներ, համարժեք բառեր կամ հնարավոր տառասխալներ օգտատիրոջ հարցման մեջ՝ ընտրելու առավել համապատասխան բովանդակությունը։ Օրինակ՝ եթե օգտատերը փնտրում է «առցանց դասընթաց», իսկ տվյալների բազայում առկա է «հեռավար ուսուցում», առաջարկեք դա որպես համապատասխան նյութ։"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել օգտատիրոջ հարցմանը ամբողջական՝ ընդգրկելով հարցման մեջ առկա բոլոր հիմնական կետերը և չավելացնելով ավելորդ տեղեկատվություն։ Օգտատիրոջ հարցմանը պատասխանելուց խուսափելով շատ կարճ կամ չափազանց երկար ու հոգնեցնող պատասխաններից։"},
            {"role": "system", "content": "Խնդրում ենք հարմարեցնել պատասխանի երկարությունը օգտատիրոջ հարցման բովանդակությանը և պահանջին․\n"
                                          "1) Եթե հարցումը պահանջում է պարզ և կարճ պատասխան, տրամադրեք համառոտ և հակիրճ տեղեկատվություն։\n"
                                          "2) Եթե հարցումը պահանջում է միջին երկարության պատասխան, պատասխանեք միջին ձևաչափով՝ ընդգրկելով բոլոր հիմնական կետերը։\n"
                                          "3) Եթե հարցումը բարդ է և պահանջում է մանրամասն բացատրություն, տրամադրեք երկար, բայց կառուցվածքային և կենտրոնացված պատասխան՝ ընդգրկելով բոլոր կարևոր մանրամասները։\n"
                                          "4) Եթե օգտատերը հատուկ նշում է պատասխանի երկարությունը (կարճ, միջին կամ երկար), հարգեք այդ պահանջը և հարմարեցրեք պատասխանի չափը նրա ցանկությանը։"},
            {"role": "system", "content": f"Տվյալների բազայի պարունակությունը հետևյալն է. {videos_content}"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել ինտուիտիվ կերպով՝ հասկանալով հաղորդագրության համատեքստը։ Խնդրում ենք ճանաչել տարբեր ձևակերպումներ, կրճատումներ կամ հնարավոր տառասխալներ, երբ օգտատերը շնորհակալություն է հայտնում կամ ավարտում է խոսակցությունը (անկախ նրանից՝ ինչ ձևակերպում կամ հապավում է օգտագործում, օրինակ՝ 'բարի', 'շնորհակալություն', 'հաջողություն', 'ցտեսություն', 'բարի շնորհակալ եմ', 'thank you', 'thanks', 'thnx', 'apres', 'merci', 'mersi', 'спасибо', 'спс'), պատասխանեք նույն լեզվով, որով նա հաղորդակցվում է։ Օրինակ՝ եթե հաղորդակցումը հայերեն է, պատասխանեք 'Ուրախ էի օգնել։ Եթե հարցեր առաջանան, պատրաստ եմ օգնելու!', եթե հաղորդակցվում է ռուսերեն՝ 'Рад был помочь! Если будут вопросы, готов помочь!', իսկ անգլերեն՝ 'Happy to help! Let me know if you have more questions!':"},
            {"role": "user", "content": f"Օգտատերը հարցնում է. {user_query}. Օգտագործելով միայն տեսանյութի տվյալները և տվյալների բազայի այլ տվյալներ՝ պատասխանեք նրա հարցմանը։"},
            {"role": "user", "content": "Պատասխանեք պարզ տեքստով և հղումները ցուցադրեք որպես սովորական տեքստ՝ առանց Markdown ձևավորման։"}
        ]

        gpt_response = await ask_gpt_async(model="gpt-4o", messages=messages)
        await message.reply(text=gpt_response)

        # Увеличиваем счетчик запросов пользователя
        await update_request_data(user_id)
    except Exception as e:
        logging.error(f"Ошибка при запросе к GPT-4o: {e}. Запрос: {message.text}")
        await message.reply("Հարցումը մշակելիս տեղի ունեցավ սխալ։ Խնդրում ենք փորձել մի փոքր ուշ։")
    finally:
        # Завершаем индикатор ввода
        try:
            typing_task.cancel()
            await typing_task
        except asyncio.CancelledError:
            pass