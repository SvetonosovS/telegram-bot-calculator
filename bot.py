from aiogram import executor
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import dp, logger


action_callback = CallbackData("move", "item_name")


choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="<", callback_data="move:<"),
            InlineKeyboardButton(text="C", callback_data="move:C"),
            InlineKeyboardButton(text="*", callback_data="move:*"),
        ],
        [
            InlineKeyboardButton(text="7", callback_data="move:7"),
            InlineKeyboardButton(text="8", callback_data="move:8"),
            InlineKeyboardButton(text="9", callback_data="move:9"),
            InlineKeyboardButton(text="/", callback_data="move:/"),
        ],
        [
            InlineKeyboardButton(text="4", callback_data="move:4"),
            InlineKeyboardButton(text="5", callback_data="move:5"),
            InlineKeyboardButton(text="6", callback_data="move:6"),
            InlineKeyboardButton(text="-", callback_data="move:-"),
        ],
        [
            InlineKeyboardButton(text="1", callback_data="move:1"),
            InlineKeyboardButton(text="2", callback_data="move:2"),
            InlineKeyboardButton(text="3", callback_data="move:3"),
            InlineKeyboardButton(text="+", callback_data="move:+"),
        ],
        [
            InlineKeyboardButton(text="0", callback_data="move:0"),
            InlineKeyboardButton(text=".", callback_data="move:."),
            InlineKeyboardButton(text="=", callback_data="move:="),
        ],
    ]
)


# функции арифметических действий
def sum_data(num_1, num_2):
    return num_1 + num_2

def sub_data(num_1, num_2):
    return num_1 - num_2

def mul_data(num_1, num_2):
    return num_1 * num_2

def div_data(num_1, num_2, par="/"):
    if num_2:
        if par == "%":
            return num_1 % num_2
        elif par == "//":
            return num_1 // num_2
        return num_1 / num_2
    else:
        return "Деление на 0 запрещено"

def pow_data(num_1, num_2=None):
    if not num_2:
        return num_1 ** 0.5
    return num_1 ** num_2

operator = {"+": sum_data, "-": sub_data, "*": mul_data, "/": div_data}
nums = ""

# старт программы
@dp.message_handler(Command("start"))
async def show_field(message: Message):
    await message.answer(text="Введите число:",
                         reply_markup=choice)

#  функция удаления последнего элемента
@dp.callback_query_handler(text_contains="<")
async def delete_char(call: CallbackQuery):
    global nums
    if nums:
        nums = nums[:-1]
        if not nums:
            await call.message.edit_text("0", reply_markup=choice)
        await call.message.edit_text(f"{nums}", reply_markup=choice)
    else:
        await call.answer(cache_time=20)
# функция стирания(обнуление)
@dp.callback_query_handler(text_contains="C")
async def erase(call: CallbackQuery):
    global nums
    nums = ""
    await call.message.edit_text("0", reply_markup=choice)


@dp.callback_query_handler(text_contains="=")
async def result(call: CallbackQuery):
    global nums
    await call.answer(cache_time=10)
    if nums:
        nums_list = nums.split()
        if len(nums_list) > 1:
            try:
                check_list = [float(i) if "." in i else int(i)
                              if i.replace(".", "", 1).isdigit()
                              else i for i in nums_list]

                ind_list = [i for i, v in enumerate(check_list) if isinstance(v, str) and v in "*/"]
            
                while ind_list:
                    k = ind_list[0]
                    a, s, b = check_list[k - 1: k + 2]
                    check_list[k - 1: k + 2] = [operator[s](a, b)]
                    ind_list = [i for i, v in enumerate(check_list) if isinstance(v, str) and v in "*/"]

                while len(check_list) > 1:
                    f, op, s = check_list[:3]
                    check_list[:3] = [operator[op](f, s)]

            except (ValueError, TypeError, KeyError):
                await call.message.edit_text("Введите значения", reply_markup=choice)
            else:
                await call.message.edit_text(f"{nums}"
                                             f" = {check_list[0]}",
                                             reply_markup=choice)
                logger.debug(f'Результат {nums} = {check_list[0]}')
            nums = ""
    else:
        logger.debug(f'Пользователь не ввел значения')
        await call.message.edit_text("Введите значения", reply_markup=choice)


@dp.callback_query_handler(action_callback.filter())
async def nums_choice(call: CallbackQuery, callback_data: dict):
    global nums

    await call.answer(cache_time=1)
    data = callback_data["item_name"]
    if data in "+-*/":
        nums += f" {data} "
    else:
        nums += data
    await call.message.edit_text(f"{nums}",
                                 reply_markup=choice)
    logger.debug(f'Пользователь ввел {nums}')


@dp.message_handler()
async def echo(message: Message):
    logger.debug('Не верный ввод пользователем')
    await message.answer(f'{message.from_user.first_name},'
                         f' ввод только с помощью кнопкок калькулятора!',
                         reply_markup=choice)

if __name__ == '__main__':
    executor.start_polling(dp)