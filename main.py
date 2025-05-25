from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import asyncio
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import *
from aiogram.types import InputFile
from aiogram.types import BufferedInputFile
from aiogram.types import URLInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
group_username='swimmingpool7'


PAYMENT_PROVIDER_TOKEN="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"
bot = Bot(token='7554225788:AAFeDqUsbQo7vjVIQub3F0O7QU1xgmS9IAc')
dp = Dispatcher()
DB_NAME = "sport_palaces.db"
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏢 Saroylar ro'yxati", callback_data="show_palaces")],
            [InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about_bot")]
        ]
    )
    return keyboard





@dp.message(CommandStart())
async def start(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
    "<b>👋 Assalomu alaykum, hurmatli foydalanuvchi!</b>\n\n"
    "🏊‍♂️ <i>Suv va sport saroylari</i> haqida barcha ma’lumotlarni bu bot orqali tez va oson topishingiz mumkin.\n\n"
    "🔹 Boshlash uchun quyidagi <b>menyudan</b> kerakli bo‘limni tanlang.\n\n"
    "⏳ Sizni kutib qolamiz!",
    parse_mode="HTML",
    reply_markup=main_menu_keyboard()
)







@dp.callback_query(F.data == "show_palaces")
async def show_palaces(callback: CallbackQuery):
    palaces = get_all_palaces()
    if not palaces:
        await callback.message.answer("🏢 Hozircha saroylar ro'yxati mavjud emas.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"palace_{palace_id}")]
            for palace_id, name in palaces
        ]
    )

    await callback.message.edit_text("🏢 Quyidagi saroylardan birini tanlang:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("palace_"))
async def show_palace_details(callback: CallbackQuery):
    palace_id = int(callback.data.split("_")[1])
    details = get_palace_details_by_id(palace_id)
    
    if not details:
        await callback.message.answer("Saroy topilmadi.")
        return

    name, location, description, lat, lon, admin_name, admin_phone, price = details
    
    text = (
        f"🏛 <b>{name}</b>\n"
        f"📍 Joylashuv: {location}\n"
        f"ℹ️ Tavsif: {description}\n"
        f"💰 Narxi (soatiga): {int(price):,} so'm\n"
        f"👨‍💼 Admin: {admin_name}\n"
        f"📞 Tel: {admin_phone}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Lokatsiya", callback_data=f"location_{palace_id}")],
        [InlineKeyboardButton(text="📝 Band qilish", callback_data=f"book_{palace_id}")],
        [InlineKeyboardButton(text="👥 Rasmiy guruhga o'tish", url="https://t.me/swimmingpool7")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="show_palaces")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")



@dp.callback_query(F.data.startswith("location_"))
async def send_location(callback: CallbackQuery):
    palace_id = int(callback.data.split("_")[1])
    details = get_palace_details_by_id(palace_id)

    if not details:
        await callback.message.answer("Lokatsiya topilmadi.")
        return

    _, _, _, lat, lon, *_ = details
    await callback.message.answer_location(latitude=lat, longitude=lon)

from aiogram.types import LabeledPrice



PAYMENT_PROVIDER_TOKEN = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"
import time

async def create_payment(price, user_id):
    prices = [LabeledPrice(label="Hovuz band qilish", amount=price * 100)]  # So'mni tiyinlarga aylantirish
    payload = f"order_{user_id}_{int(time.time())}"
    
    await bot.send_invoice(
        chat_id=user_id,
        title="Hovuz band qilish",
        description="Sizning hovuz band qilishingiz uchun to'lov.",
        payload=payload,
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="UZS",
        prices=prices,
        start_parameter="buy_pool_slot"
    )
from aiogram.fsm.state import State, StatesGroup

class BookingForm(StatesGroup):
    full_name = State()
    phone = State()
    visit_time = State()
    hours = State()
    waiting_confirmation = State()  # 

from aiogram.fsm.context import FSMContext

@dp.callback_query(F.data.startswith("book_"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    palace_id = int(callback.data.split("_")[1])
    await state.update_data(palace_id=palace_id)
    await callback.message.answer("📝 Iltimos, to‘liq ismingizni kiriting:\n\nMasalan: <b>Ali Valiyev</b>", parse_mode="HTML")
    await state.set_state(BookingForm.full_name)


@dp.message(BookingForm.full_name)
async def process_name(msg: Message, state: FSMContext):
    await state.update_data(full_name=msg.text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await msg.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)
    await state.set_state(BookingForm.phone)

@dp.message(BookingForm.phone)
async def process_phone(msg: Message, state: FSMContext):
    if not msg.contact or not msg.contact.phone_number:
        await msg.answer("❌ Telefon raqamini kontakt orqali yuboring, iltimos.")
        return

    await state.update_data(phone=msg.contact.phone_number)
    await msg.answer("📅 Borish vaqtini kiriting (masalan: 2025-05-26 15:00):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(BookingForm.visit_time)

@dp.message(BookingForm.visit_time)
async def process_visit_time(msg: Message, state: FSMContext):
    await state.update_data(visit_time=msg.text)
    await msg.answer("🕒 Necha soat davomida foydalanmoqchisiz?\n\nIltimos, soat sonini faqat raqamda kiriting (masalan: 2).")
    await state.set_state(BookingForm.hours)

@dp.message(BookingForm.hours)
async def process_hours(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("❌ Iltimos, soat sonini matn shaklida yuboring!")
        return
    
    try:
        hours = int(msg.text.strip())  
        
        if hours <= 0:
            await msg.answer("❌ Soat soni 0 dan katta bo'lishi kerak!")
            return
        
        if hours > 24: 
            await msg.answer("❌ Soat soni 24 dan oshmasligi kerak!")
            return
            
    except ValueError:
        await msg.answer("❌ Iltimos, soatni butun son shaklida kiriting (masalan: 2, 5, 8).")
        return

    await state.update_data(hours=hours)
    data = await state.get_data()

    palace_id = data.get("palace_id")
    if not palace_id:
        await msg.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan boshlang.")
        await state.clear()
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, price_per_hour FROM palaces WHERE id = ?", (palace_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            await msg.answer("❌ Hovuz topilmadi. Iltimos, qaytadan tanlang.")
            await state.clear()
            return

        palace_name = row[0]
        price_per_hour = row[1]

    except sqlite3.Error as e:
        await msg.answer("❌ Ma'lumotlar bazasida xatolik yuz berdi.")
        print(f"Database error: {e}")
        return

    payment = price_per_hour * hours

    await state.update_data(hours=hours, payment=str(payment))

    text = (
        "🏊‍♂️ *Band qilish ma'lumotlari:* \n\n"
        f"🔹 *Hovuz ID:* `{palace_id}`\n"
        f"🔹 *Hovuz nomi:* *{palace_name}*\n"
        f"🔹 *Soatlar soni:* `{hours}` soat\n"
        f"🔹 *To'lov summasi:* 💰 `{int(payment):,}` so'm\n\n"
        "👇 Quyidagilardan birini tanlang:"
    )
    
    buttons = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_booking")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_booking")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await msg.answer(text, reply_markup=keyboard, parse_mode="Markdown")








@dp.callback_query(F.data == "confirm_booking")
async def confirm_booking_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    palace_id = data.get("palace_id")
    visit_time = data.get("visit_time")
    hours = data.get("hours")
    payment = data.get("payment")
    full_name = data.get("full_name")
    phone = data.get("phone")

    if not all([palace_id, visit_time, hours, payment, full_name, phone]):
        await callback.message.answer("Buyurtma ma'lumotlari yetarli emas. Iltimos, boshidan boshlang.")
        await state.clear()
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, full_name, phone)
        VALUES (?, ?, ?)
    """, (user_id, full_name, phone))

    cursor.execute("""
        INSERT INTO bookings (palace_id, user_id, visit_time, hours, payment_amount)
        VALUES (
            ?, 
            (SELECT id FROM users WHERE telegram_id = ?), 
            ?, ?, ?
        )
    """, (palace_id, user_id, visit_time, hours, payment))

    conn.commit()
    conn.close()

    await create_payment(price=int(float(payment)), user_id=user_id)

    await callback.message.answer("✅ To‘lov uchun invoice yuborildi. To‘lovni amalga oshiring, so‘ngra buyurtma kodi sizga yuboriladi.")
    await state.clear()


@dp.callback_query(F.data == "edit_booking")
async def edit_booking_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Iltimos, qaytadan kiriting:")
    await state.set_state(BookingForm.full_name)


@dp.callback_query(F.data == "cancel_booking")
async def cancel_booking_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("✅ Band qilish bekor qilindi.")





from aiogram.types import PreCheckoutQuery

@dp.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)




def orqaga_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )




@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    user_id = message.from_user.id

    access_id = f"ACCESS{random.randint(1000, 9999)}"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET access_id = ?
        WHERE id = (
            SELECT id FROM bookings
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)
              AND access_id IS NULL
            ORDER BY id DESC LIMIT 1
        )
    """, (access_id, user_id))
    conn.commit()

    cursor.execute("""
        SELECT payment_amount, palace_id
        FROM bookings
        WHERE access_id = ?
    """, (access_id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Xatolik: bandlov topilmadi.")
        conn.close()
        return

    payment, palace_id = row

    cursor.execute("SELECT group_id, name FROM palaces WHERE id = ?", (palace_id,))
    palace_row = cursor.fetchone()
    conn.close()

    if palace_row:
        group_id, palace_name = palace_row
    else:
        group_id = None
        palace_name = "Noma'lum saroy"


    await message.answer(
        f"✅ Bandlov tasdiqlandi!\n"
        f"💵 To‘lov: {int(payment):,} so‘m\n"
        f"🧾 Maxfiy kalit: <code>{access_id}</code>",
        parse_mode="HTML",reply_markup=orqaga_button()
    )

    if group_id:
        await bot.send_message(
            chat_id=-group_id,
            text=(
                f"📢 Yangi bandlov!\n\n"
                f"Saroy: {palace_name}\n"
                f"Foydalanuvchi: @{message.from_user.username or message.from_user.full_name} (ID: {user_id})\n"
                f"To‘lov: {int(payment):,} so‘m\n"
                f"Maxfiy kalit: <code>{access_id}</code>"
            ),
            parse_mode="HTML"
        )

@dp.message(F.text == "⬅️ Orqaga")
async def back_to_main_menu(message: Message):
    await message.answer(
        "🔙 Asosiy menyuga qaytdingiz. Kerakli bo‘limni tanlang:",
        reply_markup=main_menu_keyboard()  # bu sizdagi asosiy menyu keyboard funksiyasi
    )


# --- Orqaga tugmasi uchun callback ---
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Asosiy menyu",
        reply_markup=main_menu_keyboard()
    )


@dp.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        "🤖 <b>Suv va Sport Saroylari Ma'lumot Bot</b>\n\n"
        "Ushbu bot sizga O'zbekiston bo'ylab joylashgan suv va sport saroylari haqida batafsil ma'lumot taqdim etadi.\n\n"
        "🏊‍♂️ Har bir sport saroyi haqida:\n"
        "• Joylashuvi\n"
        "• Tavsifi\n"
        "• Rasmlari\n"
        "• Qulayliklari\n"
        "haqida ma'lumot olishingiz mumkin.\n\n"
        "ℹ️ Ma'lumotlar doimiy yangilanib boriladi. Botdan foydalanib, o'zingizga eng yaqin va qulay sport majmuasini toping!",
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Asosiy menyuga qaytdingiz. Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard() 
    )




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    create_db()
    asyncio.run(main())