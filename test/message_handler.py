import asyncio
import logging
import json
from openai_requests import ask_gpt_async
from aiogram.types import Message

# Загрузка данных из videos.json
with open("videos.json", "r", encoding="utf-8") as file:
    videos_data = json.load(file)

async def ask_gpt4o(message: Message):
    # Проверяем, есть ли текст в сообщении
    if not message.text:
        await message.reply("Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել только текст:")
        return

    user_query = message.text.lower()
    if user_query in ["start", "старт", "ստարտ"]:
        user_name = message.from_user.first_name
        logging.info(f"User {user_name} отправил сообщение {user_query}")
        await message.reply(f"Բարև, {user_name}! Ինչով կարող եմ օգնել?")
        return

    async def show_typing_indicator():
        while True:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            await asyncio.sleep(2)

    typing_task = asyncio.create_task(show_typing_indicator())

    try:
        videos_content = "\n".join(
            [f"{video['title']}\n\n {video['text']}\n\n {video['link']}" for video in videos_data]
        )
        messages = [
            {"role": "system", "content": "Խնդրում ենք որոշել օգտատիրոջ հարցման լեզուն և պատասխանել այդ լեզվով։ Եթե հարցումը հայերեն է, ապա պատասխանիր հայերեն, եթե անգլերեն է՝ անգլերեն, եթե ռուսերեն է՝ ռուսերեն։"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել միայն տվյալների բազայի բովանդակությանը համապատասխան։ Եթե հարցումը չի վերաբերում տվյալների բազայի տեղեկություններին, պատասխանեք հետևյալ տեքստով՝ «Հարցման վերաբերյալ նյութեր չեն գտնվել կամ մուտքագրված հարցումն անհասկանալի է»։"},
            {"role": "system", "content": "Դուք օգնական եք, ով պատասխանում է օգտատերերի հարցերին՝ միայն տվյալների բազայի հիման վրա։ Պատասխանը պետք է ներառի համապատասխան հղումներ, եթե դրանք առկա են տվյալների բազայում։ Խնդրում ենք օգտագործել միայն տվյալների բազայի տեղեկատվությունը պատասխանների համար։ Տվյալները պարունակում են վերնագրեր, նկարագրություններ և տեսանյութերի հղումներ։"},
            {"role": "system", "content": "Խուսափեք ֆորմալ նախաբաններից։ Պատասխանեք անմիջապես և բնական ձևով։"},
            {"role": "system", "content": "Եթե օգտատիրոջ հարցմանը տվյալների բազայում ուղիղ համապատասխանություն չկա, տրամաբանորեն օգտագործեք առկա նյութերը՝ պատասխանն առավելագույնս ամբողջական և տրամաբանական դարձնելու համար։"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել ինտուիտիվ կերպով՝ հասկանալով հաղորդագրության համատեքստը։ Ճանաչեք տարբեր ձևակերպումներ, կրճատումներ, տառասխալներ, սինոնիմներ, համարժեք բառեր կամ հնարավոր տառասխալներ օգտատիրոջ հարցման մեջ՝ ընտրելու առավել համապատասխան բովանդակությունը։ Օրինակ՝ եթե օգտատերը փնտրում է «առցանց դասընթաց», իսկ տվյալների բազայում առկա է «հեռավար ուսուցում», առաջարկեք դա որպես համապատասխան նյութ։"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել օգտատիրոջ հարցմանը ամբողջական՝ ընդգրկելով հարցման մեջ առկա բոլոր հիմնական կետերը և չավելացնելով ավելորդ տեղեկատվություն։ Օգտատիրոջ հարցմանը պատասխանելուց խուսափելով շատ կարճ կամ չափազանց երկար ու հոգնեցնող պատասխաններից։"},
            {"role": "system", "content": "Խնդրում ենք հարմարեցնել պատասխանի երկարությունը օգտատիրոջ հարցման բովանդակությանը և պահանջին․\n"
                        "1) Եթե հարցումը պահանջում է պարզ և կարճ պատասխան, տրամադրեք համառոտ և հակիրճ տեղեկատվություն։\n"
                        "2) Եթե հարցումը պահանջում է միջին երկարության պատասխան, պատասխանեք միջին ձևաչափով՝ ընդգրկելով բոլոր հիմնական կետերը։\n"
                        "3) Եթե հարցումը բարդ է և պահանջում է մանրամասն բացատրություն, տրամադրեք երկար, բայց կառուցվածքային և կենտրոնացված պատասխան՝ ընդգրկելով բոլոր կարևոր մանրամասները։\n"
                        "4) Եթե օգտատերը հատուկ նշում է պատասխանի երկարությունը (կարճ, միջին կամ երկար), հարգեք այդ պահանջը և հարմարեցրեք պատասխանի չափը նրա ցանկությանը։"},
            {"role": "system", "content": f"Տվյալների բազայի պարունակությունը հետևյալն է. {videos_content}"},
            {"role": "system", "content": "Խնդրում ենք պատասխանել ինտուիտիվ կերպով՝ հասկանալով հաղորդագրության համատեքստը։ Խնդրում ենք ճանաչել տարբեր ձևակերպումներ, կրճատումներ կամ հնարավոր տառասխալներ, երբ օգտատերը շնորհակալություն է հայտնում կամ ավարտում է խոսակցությունը (անկախ նրանից՝ ինչ ձևակերպում կամ հապավում է օգտագործում, օրինակ՝ 'բարի', 'շնորհակալություն', 'բարի շնորհակալ եմ', 'thank you', 'thanks', 'thnx', 'apres', 'merci', 'mersi', 'спасибо', 'спс'), պատասխանեք նույն լեզվով, որով նա հաղորդակցվում է։ Օրինակ՝ եթե հաղորդակցումը հայերեն է, պատասխանեք 'Ուրախ էի օգնել։ Եթե հարցեր առաջանան, պատրաստ եմ օգնելու!', եթե հաղորդակցվում է ռուսերեն՝ 'Рад был помочь! Если будут вопросы, готов помочь!', իսկ անգլերեն՝ 'Happy to help! Let me know if you have more questions!':"},
            {"role": "user", "content": f"Օգտատերը հարցնում է. {user_query}. Օգտագործելով միայն տեսանյութի տվյալները և տվյալների բազայի այլ տվյալներ՝ պատասխանեք նրա հարցմանը։"},
            {"role": "user", "content": "Պատասխանեք պարզ տեքստով և հղումները ցուցադրեք որպես սովորական տեքստ՝ առանց Markdown ձևավորման։"}
        ]

        gpt_response = await ask_gpt_async(model="gpt-4o", messages=messages)
        typing_task.cancel()
        await message.reply(text=gpt_response)

    except Exception as e:
        typing_task.cancel()
        logging.error(f"Ошибка при запросе к GPT-4o: {e}")
        await message.reply("Ձեր հարցումը մշակելիս սխալ տեղի ունեցավ: Խնդրում ենք փորձել մի փոքր ուշ:")
