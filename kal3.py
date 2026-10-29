import discord
from discord.ext import commands, tasks
from discord.ui import Modal, InputText, View, Button, Select
import time
import asyncio
import json
import os
import random
import logging
import re
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta

import aiohttp
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123")

# ============================================================
# КОНФИГ
# ============================================================
ИМЯ_БОТА = "Don Core"
ИМЯ_СЕМЬИ = "La Famiglia"

ФАЙЛ_ДАННЫХ = "bot_data.json"
ФАЙЛ_НАСТРОЕК = "bot_settings.json"
ФАЙЛ_НАКАЗАНИЙ = "punishments.json"
ФАЙЛ_ПОКЕРА = "poker_tables.json"

РОЛЬ_СЕКРЕТНАЯ = "Capo di Tutti Capi"
РОЛЬ_ВЕРИФИЦИРОВАН = "Verified"

ROBLOX_API = "https://users.roblox.com/v1"
ПРЕФИКС_КОДА = "FAM-"
ВРЕМЯ_КОДА = 600

ПОРОГИ_XP = [4600, 7850, 13500, 46000, 100000]
КД_XP = 45
КД_МИССИЯ_СООБЩ = 30
КД_КАЗИНО = 3

НАГРАДА_ДЕЙЛИ = 500
БОНУС_STREAK = 100
МАКС_МНОЖИТЕЛЬ = 3
КД_ДЕЙЛИ = 20 * 3600
СБРОС_ДЕЙЛИ = 48 * 3600

ТАЙМАУТ_ДУЭЛИ = 60
КД_ПЕРЕВОДА = 5

КАНАЛ_ЛОГОВ = "bot-logs"
КАНАЛ_CHANGELOG = "changelog"
КАНАЛ_ПРЕДЛОЖЕНИЙ = "suggestions"
КАНАЛ_БАГОВ_ИГРЫ = "game-bugs-report"
КАНАЛ_БАГОВ_СЕРВЕРА = "server-bugs-report"

ПЛОХИЕ_СЛОВА = [
    "бля", "хуй", "хуе", "пизд", "ебат", "ебал", "ебан", "еби",
    "сука", "сучк", "мраз", "гандон", "долбоеб", "пидор", "пидар",
    "мудак", "мразь", "нахуй", "похуй", "охуе", "ахуе", "залуп",
    "манд", "шлюх", "ублюд", "гнид", "козл", "козёл",
    "fuck", "shit", "bitch", "dick", "pussy", "cunt", "bastard",
]
ПОРОГ_СПАМА = 17
ОКНО_СПАМА = 60
ЧАСОВ_МУТА = 1

ИМЕНА_РОЛЕЙ = {
    1: "Associato", 2: "Soldato", 3: "Capodecina",
    4: "Sottocapo", 5: "Consigliere",
}
ОТОБРАЖЕНИЕ_РАНГОВ = {
    0: "Forestiero", 1: "Associato", 2: "Soldato", 3: "Capodecina",
    4: "Sottocapo", 5: "Consigliere", 6: "👑 Capo di Tutti Capi",
}
ЦВЕТА_РАНГОВ = {
    0: discord.Color.light_grey(), 1: discord.Color.dark_grey(),
    2: discord.Color.darker_grey(), 3: discord.Color.dark_blue(),
    4: discord.Color.dark_purple(), 5: discord.Color.dark_gold(),
    6: discord.Color.gold(),
}

ТОВАРЫ = {
    "made_man": {"label": "Made Man", "price": 15000, "role_name": "Made Man",
                 "emoji": "🎩", "desc_key": "shop_made_man"},
    "consigliere_role": {"label": "Consigliere", "price": 50000,
                         "role_name": "Consigliere",
                         "emoji": "🧠", "desc_key": "shop_consigliere"},
    "capo_role": {"label": "Capo Famiglia", "price": 100000,
                  "role_name": "Capo Famiglia",
                  "emoji": "👑", "desc_key": "shop_capo"},
    "padrino": {"label": "Title «Padrino»", "price": 7500, "role_name": None,
                "emoji": "🙏", "desc_key": "shop_padrino"},
    "il_lupo": {"label": "Title «Il Lupo»", "price": 5000, "role_name": None,
                "emoji": "🐺", "desc_key": "shop_lupo"},
    "il_serpente": {"label": "Title «Il Serpente»", "price": 5000, "role_name": None,
                    "emoji": "🐍", "desc_key": "shop_serpente"},
    "il_fantasma": {"label": "Title «Il Fantasma»", "price": 10000, "role_name": None,
                    "emoji": "👻", "desc_key": "shop_fantasma"},
    "profile_bg": {"label": "Profile background slot", "price": 5000,
                   "role_name": None, "emoji": "🖼️", "desc_key": "shop_bg"},
}

ВСЕ_РОЛИ_БОТА = list(ИМЕНА_РОЛЕЙ.values()) + [РОЛЬ_СЕКРЕТНАЯ] + \
    [item["role_name"] for item in ТОВАРЫ.values() if item["role_name"]]

ДОСТИЖЕНИЯ = {
    "top1":     {"name_key": "ach_top1", "xp": 15000, "desc_key": "ach_top1_d"},
    "rank5":    {"name_key": "ach_rank5", "xp": 15000, "desc_key": "ach_rank5_d"},
    "jackpot":  {"name_key": "ach_jackpot", "xp": 10000, "desc_key": "ach_jackpot_d"},
    "verified": {"name_key": "ach_verified", "xp": 5000, "desc_key": "ach_verified_d"},
    "rich":     {"name_key": "ach_rich", "xp": 7000, "desc_key": "ach_rich_d"},
}

ЯЗЫКИ = {"en": "🇬🇧 English", "ru": "🇷🇺 Русский"}
ЯЗЫК_ПО_УМОЛЧАНИЮ = "en"

СТРОКИ = {
    "close_btn":       {"en": "Close", "ru": "Chiudi"},
    "pk_btn_fold":     {"en": "Fold", "ru": "Сбросить"},
    "pk_btn_check":    {"en": "Check", "ru": "Пропустить"},
    "pk_btn_call":     {"en": "Call {n}", "ru": "Уравнять {n}"},
    "pk_btn_raise":    {"en": "Raise…", "ru": "Поднять…"},
    "pk_btn_allin":    {"en": "ALL-IN {n}", "ru": "ВА-БАНК {n}"},
    "pk_modal_raise":  {"en": "🔥 Raise", "ru": "🔥 Поднять"},
    "cancel_btn":      {"en": "Cancel", "ru": "Отмена"},
    "lang_title":      {"en": "🌐 Choose your interface language:", "ru": "🌐 Выбери язык интерфейса:"},
    "lang_current":    {"en": "🌐 Current language: **{lang}**", "ru": "🌐 Текущий язык: **{lang}**"},
    "lang_changed":    {"en": "✅ Language changed to **{lang}**", "ru": "✅ Язык изменён на **{lang}**"},
    "don_welcome":     {"en": "🎩 **{bot} welcomes you, {family}**\n\n*Benvenuto. Here the family rules.*", "ru": "🎩 **{bot} приветствует тебя, {family}**\n\n*Benvenuto. Здесь решает семья.*"},
    "btn_profile":     {"en": "Profile", "ru": "Досье"},
    "btn_admin":       {"en": "Don's office", "ru": "Кабинет Дона"},
    "wallet_title":    {"en": "💰 Wallet", "ru": "💰 Кошелёк"},
    "wallet_have":     {"en": "You have **{amount}** 💰", "ru": "У вас **{amount}** 💰"},
    "daily_title":     {"en": "💰 Tribute collected!", "ru": "💰 Дань собрана!"},
    "daily_got":       {"en": "Received", "ru": "Получено"},
    "daily_streak":    {"en": "Streak", "ru": "Streak"},
    "daily_next":      {"en": "📈 Next in 20 hours.", "ru": "📈 Следующая через 20 часов."},
    "daily_hint":      {"en": "💡 Claim XP bonus in `/missions`", "ru": "💡 Забрать бонус XP — в `/missions`"},
    "daily_cooldown":  {"en": "⏳ Next tribute in **{h}h {m}m**.\nStreak: **{streak}** 🔥", "ru": "⏳ Следующая дань через **{h}ч {m}м**.\nStreak: **{streak}** 🔥"},
    "casino_opened":   {"en": "🎲 **{user} opened the underground casino!**", "ru": "🎲 **{user} открыл подпольное казино!**"},
    "casino_wallet":   {"en": "💰 Your wallet", "ru": "💰 Ваш кошелёк"},
    "casino_pick":     {"en": "Choose your bet:", "ru": "Выберите ставку:"},
    "casino_spin":     {"en": "🎲 **{user} plays for `{amount}` 💰**\n\n🔄 Dice rolling...\n`[ 🎩 | 🎩 | 🎩 ]`", "ru": "🎲 **{user} играет на `{amount}` 💰**\n\n🔄 Кости катаются...\n`[ 🎩 | 🎩 | 🎩 ]`"},
    "casino_stop":     {"en": "🎲 **{user} plays for `{amount}` 💰**\n\n🔄 Stopping...\n`[ 🎩 | 🔄 | 🎩 ]`", "ru": "🎲 **{user} играет на `{amount}` 💰**\n\n🔄 Останавливаются...\n`[ 🎩 | 🔄 | 🎩 ]`"},
    "casino_jackpot":  {"en": "🌟 **JACKPOT! x10** 🌟", "ru": "🌟 **ДЖЕКПОТ! x10** 🌟"},
    "casino_bigwin":   {"en": "🔥 **Big win! x5** 🔥", "ru": "🔥 **Большой куш! x5** 🔥"},
    "casino_win":      {"en": "🎉 **Victory! x2** 🎉", "ru": "🎉 **Победа! x2** 🎉"},
    "casino_lose":     {"en": "💀 **Defeat!**", "ru": "💀 **Проигрыш!**"},
    "casino_no_money": {"en": "❌ No money to bet!", "ru": "❌ Нет денег для ставки!"},
    "casino_not_en":   {"en": "❌ Not enough! Balance: `{balance}` 💰", "ru": "❌ Недостаточно! Баланс: `{balance}` 💰"},
    "casino_cd":       {"en": "⏳ Wait {sec:.1f} sec!", "ru": "⏳ Подожди {sec:.1f} сек!"},
    "casino_not_yours":{"en": "❌ Not your table!", "ru": "❌ Это не ваш стол!"},
    "casino_res_win":  {"en": "{tier}\n🎲 Result: `[ 🎩 | 🎩 | 🎩 ]` (x{mult})\n💰 {user}: **+{profit}**\n💳 Balance: **{balance}** 💰{role_msg}", "ru": "{tier}\n🎲 Итог: `[ 🎩 | 🎩 | 🎩 ]` (x{mult})\n💰 {user}: **+{profit}**\n💳 Баланс: **{balance}** 💰{role_msg}"},
    "casino_res_lose": {"en": "{title}\n🎲 Result: `[ 🎩 | ❌ | 🎩 ]`\n💸 {user} lost **-{amount}**\n💳 Balance: **{balance}** 💰", "ru": "{title}\n🎲 Итог: `[ 🎩 | ❌ | 🎩 ]`\n💸 {user} потерял **-{amount}**\n💳 Баланс: **{balance}** 💰"},
    "m_title":         {"en": "📋 Family business", "ru": "📋 Дела семьи"},
    "m_claimed":       {"en": "✅ Claimed", "ru": "✅ Забрано"},
    "m_ready":         {"en": "🟢 Ready!", "ru": "🟢 Готово!"},
    "m_l1":            {"en": "**1.** Talk to family (5 msgs)", "ru": "**1.** Связь с семьёй (5 сообщ.)"},
    "m_l2":            {"en": "**2.** Reports (3 videos/gifs)", "ru": "**2.** Донесения (3 видео/гифки)"},
    "m_l3":            {"en": "**3.** Casino games (3)", "ru": "**3.** Игры в казино (3)"},
    "m_l4":            {"en": "**4.** Casino wins (3)", "ru": "**4.** Побед в казино (3)"},
    "m_l5":            {"en": "**5.** Win a showdown", "ru": "**5.** Победа в разборке"},
    "m_l6":            {"en": "**6.** Transfer money", "ru": "**6.** Перевод денег"},
    "m_l7":            {"en": "**7.** Buy on black market", "ru": "**7.** Покупка на рынке"},
    "m_l8":            {"en": "**8.** Vote in a poll", "ru": "**8.** Голос в опросе"},
    "m_l9":            {"en": "**9.** Roll /roll ≥90", "ru": "**9.** Кинуть /roll ≥90"},
    "m_l10":           {"en": "**10.** Collect /daily", "ru": "**10.** Собрать дань (/daily)"},
    "m_l11":           {"en": "**11.** Furry trigger", "ru": "**11.** Триггер «фурри»"},
    "m_l12":           {"en": "**12.** Hardcore 10 000 XP", "ru": "**12.** Хардкор 10 000 XP"},
    "m_footer":        {"en": "Rewards: 500 – 10 000 💰 + XP", "ru": "Награды: 500 – 10 000 💰 + XP"},
    "m_claimed_ok":    {"en": "🎉 **Fatto!** Claimed: **+{coins}** 💰 and **+{xp}** XP!", "ru": "🎉 **Fatto!** Забрано: **+{coins}** 💰 и **+{xp}** XP!"},
    "m_no_rewards":    {"en": "❌ No rewards available.", "ru": "❌ Нет доступных наград."},
    "m_not_yours":     {"en": "❌ Not your business.", "ru": "❌ Это не ваши дела."},
    "ach_title_own":   {"en": "🏆 Achievements — {name}", "ru": "🏆 Достижения — {name}"},
    "ach_locked":      {"en": "🔒", "ru": "🔒"},
    "ach_unlocked":    {"en": "✅", "ru": "✅"},
    "ach_total":       {"en": "Unlocked: `{have}/{total}`", "ru": "Открыто: `{have}/{total}`"},
    "ach_new":         {"en": "🏆 NEW ACHIEVEMENT!", "ru": "🏆 НОВОЕ ДОСТИЖЕНИЕ!"},
    "ach_member":      {"en": "Family member", "ru": "Член семьи"},
    "ach_reward":      {"en": "Reward", "ru": "Награда"},
    "ach_dm":          {"en": "🏆 **Achievement unlocked!**\n\n{name} — *{desc}*\nReward: **+{xp} XP**", "ru": "🏆 **Достижение получено!**\n\n{name} — *{desc}*\nНаграда: **+{xp} XP**"},
    "top_title":       {"en": "🎩 Family registry — {cat}", "ru": "🎩 Реестр семьи — {cat}"},
    "top_empty":       {"en": "📭 Empty.", "ru": "📭 Пусто."},
    "top_xp":          {"en": "XP", "ru": "XP"},
    "top_money":       {"en": "Money", "ru": "Деньги"},
    "top_casino":      {"en": "Casino", "ru": "Казино"},
    "top_msgs":        {"en": "Messages", "ru": "Сообщения"},
    "prof_title":      {"en": "🎩 Profile — {name}", "ru": "🎩 Досье — {name}"},
    "prof_xp_money":   {"en": "**XP:** `{xp}` | **Money:** `{coins}` 💰", "ru": "**XP:** `{xp}` | **Деньги:** `{coins}` 💰"},
    "prof_rank":       {"en": "**Rank:** {rank}", "ru": "**Ранг:** {rank}"},
    "prof_until_next": {"en": "📈 Until next rank: `{xp} XP`", "ru": "📈 До следующего ранга: `{xp} XP`"},
    "prof_max":        {"en": "🎩 You're Consigliere — the Don's right hand", "ru": "🎩 Вы Consigliere — правая рука Дона"},
    "prof_title_l":    {"en": "👑 Title: **{title}**", "ru": "👑 Титул: **{title}**"},
    "prof_roblox":     {"en": "🔗 Roblox: **{nick}**", "ru": "🔗 Roblox: **{nick}**"},
    "prof_ach":        {"en": "🏆 Achievements: `{have}/{total}`", "ru": "🏆 Достижений: `{have}/{total}`"},
    "prof_refresh":    {"en": "Aggiorna", "ru": "Aggiorna"},
    "prof_close":      {"en": "Chiudi", "ru": "Chiudi"},
    "shop_title":      {"en": "🛒 Black market", "ru": "🛒 Чёрный рынок"},
    "shop_wallet":     {"en": "💰 Your wallet: **{coins}**", "ru": "💰 Ваш кошелёк: **{coins}**"},
    "shop_placeholder":{"en": "Choose an item...", "ru": "Выберите товар..."},
    "shop_bought":     {"en": "✅ **Fatto!** Purchased: **{item}** for **{price}** 💰", "ru": "✅ **Fatto!** Куплено: **{item}** за **{price}** 💰"},
    "shop_no_money":   {"en": "❌ Need **{price}** 💰, you have **{have}** 💰.", "ru": "❌ Нужно **{price}** 💰, у вас **{have}** 💰."},
    "shop_owned":      {"en": "❌ Already owned!", "ru": "❌ Уже куплено!"},
    "shop_not_yours":  {"en": "❌ Not your market!", "ru": "❌ Это не ваш магазин!"},
    "shop_bg_ok":      {"en": "✅ **Fatto!** Background slot purchased.\nUse `/setbg <URL>` to set it.", "ru": "✅ **Fatto!** Слот под фон куплен.\nИспользуй `/setbg <URL>` чтобы поставить."},
    "shop_role_missing":{"en": "❌ Role `{role}` not found.", "ru": "❌ Роль `{role}` не найдена."},
    "shop_role_given":{"en": "✅ **Fatto!** Role **{role}** granted.", "ru": "✅ **Fatto!** Выдана роль **{role}**."},
    "shop_made_man":   {"en": "Full member of the family", "ru": "Полноправный член семьи"},
    "shop_consigliere":{"en": "The Don's advisor", "ru": "Советник Дона"},
    "shop_capo":       {"en": "Head of the family", "ru": "Глава семьи"},
    "shop_padrino":    {"en": "Godfather", "ru": "Крёстный отец"},
    "shop_lupo":       {"en": "The Wolf — predator", "ru": "Волк — хищник"},
    "shop_serpente":   {"en": "The Snake — cunning", "ru": "Змей — хитрец"},
    "shop_fantasma":   {"en": "The Ghost — elusive", "ru": "Призрак — неуловимый"},
    "shop_bg":         {"en": "Unlocks /setbg for custom profile bg", "ru": "Разблокирует /setbg для кастомного фона"},
    "duel_title":      {"en": "⚔️ **Showdown!**\n\n{ch} **challenges** {tg}\nBet: **{amount}** 💰\n\n{tg}, accept or decline (60 sec):", "ru": "⚔️ **Разборка!**\n\n{ch} **вызывает** {tg}\nСтавка: **{amount}** 💰\n\n{tg}, прими или уклонись (60 сек):"},
    "duel_accept":     {"en": "✅ Accept", "ru": "✅ Принять"},
    "duel_decline":    {"en": "❌ Decline", "ru": "❌ Отклонить"},
    "duel_not_yours":  {"en": "❌ Not your showdown.", "ru": "❌ Это не ваша разборка."},
    "duel_ended":      {"en": "❌ Already finished.", "ru": "❌ Завершена."},
    "duel_ch_no_money":{"en": "❌ <@{ch}> has no **{amount}** 💰.", "ru": "❌ У <@{ch}> нет **{amount}** 💰."},
    "duel_tg_no_money":{"en": "❌ You don't have **{amount}** 💰!", "ru": "❌ У вас нет **{amount}** 💰!"},
    "duel_result":     {"en": "⚔️ **Showdown!**\n\n{ch} **vs** {tg}\nBet: **{amount}** 💰\n\n🎩 Winner: <@{win}>! Takes **+{amount}** 💰", "ru": "⚔️ **Разборка!**\n\n{ch} **vs** {tg}\nСтавка: **{amount}** 💰\n\n🎩 Победил: <@{win}>! Забирает **+{amount}** 💰"},
    "duel_declined":   {"en": "❌ <@{tg}> declined. Codardo!", "ru": "❌ <@{tg}> уклонился. Codardo!"},
    "duel_bad_target": {"en": "❌ Bad opponent.", "ru": "❌ Некорректный оппонент."},
    "duel_bad_bet":    {"en": "❌ Bet must be positive.", "ru": "❌ Ставка положительная."},
    "duel_no_money":   {"en": "❌ You don't have **{amount}** 💰.", "ru": "❌ У вас нет **{amount}** 💰."},
    "tr_ok":           {"en": "✅ **Fatto!**\n{sender} → {receiver}\nAmount: **{amount}** 💰", "ru": "✅ **Fatto!**\n{sender} → {receiver}\nСумма: **{amount}** 💰"},
    "tr_cd":           {"en": "⏳ Wait {sec:.1f} sec.", "ru": "⏳ Aspetta {sec:.1f} сек."},
    "tr_no_money":     {"en": "❌ Not enough. Balance: **{balance}** 💰", "ru": "❌ Недостаточно. Баланс: **{balance}** 💰"},
    "ver_title":       {"en": "🔗 Verifica Roblox", "ru": "🔗 Verifica Roblox"},
    "ver_label":       {"en": "Your Roblox username", "ru": "Ваш Roblox username"},
    "ver_placeholder": {"en": "Nick without @", "ru": "Ник без @"},
    "ver_already":     {"en": "✅ Already verified as **{nick}**.", "ru": "✅ Уже верифицированы как **{nick}**."},
    "ver_not_found":   {"en": "❌ Nick not found on Roblox.", "ru": "❌ Ник не найден в Roblox."},
    "ver_step2":       {"en": "🔐 Step 2: Ownership proof", "ru": "🔐 Шаг 2: Подтверждение"},
    "ver_step2_desc":  {"en": "**1.** Open: https://www.roblox.com/users/{rid}/profile\n**2.** «...» → **About**.\n**3.** Paste this code into your bio:\n\n```\n{code}\n```\n**4.** Save and click the button.\n\n⏳ **10 minutes**.", "ru": "**1.** Откройте: https://www.roblox.com/users/{rid}/profile\n**2.** «...» → **About**.\n**3.** Вставьте код в описание:\n\n```\n{code}\n```\n**4.** Сохраните и жмите кнопку.\n\n⏳ **10 минут**."},
    "ver_check":       {"en": "✅ Check", "ru": "✅ Проверить"},
    "ver_expired":     {"en": "❌ Code expired. `/verify`", "ru": "❌ Код истёк. `/verify`"},
    "ver_no_profile":  {"en": "❌ Couldn't fetch profile.", "ru": "❌ Не удалось получить профиль."},
    "ver_not_found_code":{"en": "❌ Code not found. Make sure `{code}` is saved in bio.", "ru": "❌ Код не найден. Убедитесь: `{code}` сохранён в описании."},
    "ver_success":     {"en": "🎩 **Benvenuto in famiglia!**\nRoblox: **{nick}** (`{rid}`)\nRole `{role}` granted.", "ru": "🎩 **Benvenuto in famiglia!**\nRoblox: **{nick}** (`{rid}`)\nРоль `{role}` выдана."},
    "warn_done":       {"en": "⚠️ **Attenzione!** {user} warned.\n**Reason:** {reason}", "ru": "⚠️ **Attenzione!** {user} предупреждён.\n**Причина:** {reason}"},
    "warn_dm":         {"en": "⚠️ Warning on **{guild}**.\nReason: {reason}", "ru": "⚠️ Предупреждение на **{guild}**.\nПричина: {reason}"},
    "mute_done":       {"en": "🔇 **Silenzio!** {user} for **{dur}**.\n**Reason:** {reason}", "ru": "🔇 **Silenzio!** {user} на **{dur}**.\n**Причина:** {reason}"},
    "mute_dm":         {"en": "🔇 Timeout for **{dur}** on **{guild}**.\nReason: {reason}", "ru": "🔇 Мут на **{dur}** на **{guild}**.\nПричина: {reason}"},
    "unmute_done":     {"en": "🔊 {user} can speak again.", "ru": "🔊 {user} снова может говорить."},
    "kick_done":       {"en": "👢 {user} kicked.\n**Reason:** {reason}", "ru": "👢 {user} изгнан.\n**Причина:** {reason}"},
    "kick_dm":         {"en": "👢 You were kicked from **{guild}**.\nReason: {reason}", "ru": "👢 Тебя изгнали из **{guild}**.\nПричина: {reason}"},
    "ban_done":        {"en": "🔨 {user} banned forever.\n**Reason:** {reason}\n**Forgive:** `/unban {uid}`", "ru": "🔨 {user} изгнан навсегда.\n**Причина:** {reason}\n**Простить:** `/unban {uid}`"},
    "ban_dm":          {"en": "🔨 You were banned from **{guild}**.\nReason: {reason}", "ru": "🔨 Ты забанен на **{guild}**.\nПричина: {reason}"},
    "unban_done":      {"en": "✅ **{user}** forgiven.\n**Reason:** {reason}", "ru": "✅ **{user}** прощён.\n**Причина:** {reason}"},
    "hist_title":      {"en": "📜 Dossier — {name}", "ru": "📜 Досье — {name}"},
    "hist_empty":      {"en": "✅ {user} has clean record.", "ru": "✅ У {user} чистая репутация."},
    "hist_reason":     {"en": "Reason", "ru": "Причина"},
    "hist_mod":        {"en": "Moderator", "ru": "Модератор"},
    "hist_total":      {"en": "Total: {n}", "ru": "Всего: {n}"},
    "hist_auto":       {"en": "Don Core (auto)", "ru": "Don Core (авто)"},
    "hist_expired":    {"en": "(expired)", "ru": "(истёк)"},
    "am_warn":         {"en": "⚠️ {user}, **Attenzione!** Family doesn't like this (**{reason}**). One more — **Silenzio** for {h}h.", "ru": "⚠️ {user}, **Attenzione!** Семья не одобряет (**{reason}**). Ещё раз — **Silenzio** на {h} ч."},
    "am_mute":         {"en": "🔇 **Silenzio!** {user} muted for **{h}h**. Family doesn't repeat.", "ru": "🔇 **Silenzio!** {user} на **{h} ч**. Семья не повторяет."},
    "am_violation_t":  {"en": "⚠️ Attenzione — violation", "ru": "⚠️ Attenzione — нарушение"},
    "am_who":          {"en": "Who", "ru": "Кто"},
    "am_where":        {"en": "Where", "ru": "Где"},
    "am_reason":       {"en": "Reason", "ru": "Причина"},
    "am_nth":          {"en": "Violation #{n} today", "ru": "Нарушение №{n} за сегодня"},
    "am_action_warn":  {"en": "Action: warning", "ru": "Действие: предупреждение"},
    "am_action_mute":  {"en": "Silenzio {h}h", "ru": "Silenzio {h} ч"},
    "am_cant_mute":    {"en": "Action: couldn't mute", "ru": "Действие: не удалось замутить"},
    "botlog_protect":  {"en": "🚫 {user}, this channel is for bot logs only.", "ru": "🚫 {user}, этот канал только для логов бота."},
    "botlog_expired":  {"en": "🔊 Silenzio expired", "ru": "🔊 Silenzio истёк"},
    "botlog_exp_dur":  {"en": "Duration was: {dur}", "ru": "Срок был: {dur}"},
    "bug_title_g":     {"en": "🐛 Bug report (Game)", "ru": "🐛 Баг-репорт (Игра)"},
    "bug_title_s":     {"en": "🐛 Bug report (Server)", "ru": "🐛 Баг-репорт (Сервер)"},
    "bug_name":        {"en": "Short title", "ru": "Краткое название"},
    "bug_name_ph":     {"en": "e.g. button X doesn't work", "ru": "Например: не работает кнопка X"},
    "bug_desc":        {"en": "Description", "ru": "Описание"},
    "bug_desc_ph":     {"en": "What's wrong?", "ru": "Что не так?"},
    "bug_steps":       {"en": "Steps to reproduce", "ru": "Шаги воспроизведения"},
    "bug_steps_ph":    {"en": "1. Opened... 2. Clicked... 3. Saw...", "ru": "1. Открыл... 2. Нажал... 3. Увидел..."},
    "bug_channel_no":  {"en": "❌ Bug channel `{ch}` not found.", "ru": "❌ Канал для багов `{ch}` не найден."},
    "bug_created":     {"en": "✅ Report created: {url}", "ru": "✅ Донесение создано: {url}"},
    "bug_reporter":    {"en": "Reporter", "ru": "Доносчик"},
    "bug_type":        {"en": "Type", "ru": "Тип"},
    "bug_type_g":      {"en": "Game", "ru": "Игра"},
    "bug_type_s":      {"en": "Server", "ru": "Сервер"},
    "bug_status":      {"en": "Status", "ru": "Статус"},
    "bug_open":        {"en": "🆕 Open", "ru": "🆕 Новое"},
    "bug_wip":         {"en": "🔧 In progress", "ru": "🔧 В работе"},
    "bug_fixed":       {"en": "✅ Fixed", "ru": "✅ Готово"},
    "bug_rejected":    {"en": "❌ Rejected", "ru": "❌ Отклонено"},
    "bug_no_access":   {"en": "❌ Don or author only.", "ru": "❌ Только Дон или автор."},
    "sug_title":       {"en": "💡 Suggestion to the family", "ru": "💡 Предложение семье"},
    "sug_label":       {"en": "Your idea", "ru": "Ваша идея"},
    "sug_ph":          {"en": "What would you suggest?", "ru": "Что предлагаешь?"},
    "sug_no_log":      {"en": "❌ Log channel `#bot-logs` not found.", "ru": "❌ Канал логов (`#bot-logs`) не найден."},
    "sug_sent":        {"en": "✅ Sent to the Don for review.", "ru": "✅ Донесение отправлено Дону."},
    "sug_pending":     {"en": "💡 Suggestion (pending Don's review)", "ru": "💡 Предложение (на рассмотрении Дона)"},
    "sug_approve":     {"en": "✅ Approve", "ru": "✅ Одобрить"},
    "sug_reject":      {"en": "❌ Reject", "ru": "❌ Отклонить"},
    "sug_don_only":    {"en": "❌ Don only.", "ru": "❌ Только Дон."},
    "sug_processed":   {"en": "❌ Already processed.", "ru": "❌ Уже обработано."},
    "sug_pub_title":   {"en": "💡 Family suggestion", "ru": "💡 Предложение семьи"},
    "sug_published":   {"en": "✅ Published: {url}", "ru": "✅ Опубликовано: {url}"},
    "sug_rejected":    {"en": "❌ Rejected.", "ru": "❌ Отклонено."},
    "sug_channel_no":  {"en": "❌ Channel `#{ch}` not found.", "ru": "❌ Канал `#{ch}` не найден."},
    "cl_don_only":     {"en": "❌ Don only.", "ru": "❌ Только Дон."},
    "cl_channel_no":   {"en": "❌ Channel `#{ch}` not found.", "ru": "❌ Канал `#{ch}` не найден."},
    "cl_update":       {"en": "📦 Update {v}", "ru": "📦 Обновление {v}"},
    "cl_published":    {"en": "✅ Published to {ch}", "ru": "✅ Опубликовано в {ch}"},
    "adm_pass_title":  {"en": "🔐 Don's office login", "ru": "🔐 Вход в кабинет Дона"},
    "adm_pass_label":  {"en": "Don's password", "ru": "Пароль Дона"},
    "adm_pass_ph":     {"en": "Enter password...", "ru": "Введите пароль..."},
    "adm_wrong_pass":  {"en": "❌ Wrong password!", "ru": "❌ Неверный пароль!"},
    "adm_welcome":     {"en": "✅ **Benvenuto, Don.** Family control panel:", "ru": "✅ **Benvenuto, Don.** Панель управления семьёй:"},
    "adm_btn_react":   {"en": "Auto-reactions", "ru": "Авто-реакции"},
    "adm_btn_ranks":   {"en": "Ranks", "ru": "Звания"},
    "adm_btn_roles":   {"en": "Roles", "ru": "Роли"},
    "adm_btn_money":   {"en": "Money", "ru": "Деньги"},
    "adm_btn_abuse":   {"en": "Don's broadcast", "ru": "Рассылка Дона"},
    "adm_btn_xp":      {"en": "Give XP", "ru": "Выдать XP"},
    "adm_btn_bot":     {"en": "Don Core profile", "ru": "Профиль Don Core"},
    "adm_btn_logs":    {"en": "Protect #bot-logs", "ru": "Защита #bot-logs"},
    "react_title":     {"en": "⚙️ Auto-reactions", "ru": "⚙️ Авто-реакции"},
    "react_who":       {"en": "Track who?", "ru": "Кого отслеживать?"},
    "react_who_ph":    {"en": "'all' / ID / <@id>", "ru": "'all' / ID / <@id>"},
    "react_emojis":    {"en": "Emojis (space-separated)", "ru": "Эмодзи через пробел"},
    "react_emojis_ph": {"en": "🇮 🇹 🇦 or 🎩", "ru": "🇮 🇹 🇦 или 🎩"},
    "react_no_emoji":  {"en": "❌ No emojis specified.", "ru": "❌ Укажите эмодзи."},
    "react_saved":     {"en": "✅ **Fatto!**\n🎯 `{target}`\n🎨 `{emojis}`", "ru": "✅ **Fatto!**\n🎯 `{target}`\n🎨 `{emojis}`"},
    "give_coins_t":    {"en": "💰 Give money", "ru": "💰 Выдача денег"},
    "give_xp_t":       {"en": "⭐ Give XP", "ru": "⭐ Выдача XP"},
    "give_who":        {"en": "To whom?", "ru": "Кому?"},
    "give_who_ph":     {"en": "ID / 'all' / role name", "ru": "ID / 'all' / название роли"},
    "give_amount":     {"en": "How much?", "ru": "Сколько?"},
    "give_amount_ph":  {"en": "e.g. 1000 (or -500 to take)", "ru": "Например: 1000 (или -500 чтобы отнять)"},
    "give_number":     {"en": "❌ Number, please.", "ru": "❌ Число, пожалуйста."},
    "give_positive":   {"en": "❌ Amount must be positive.", "ru": "❌ Сумма положительная."},
    "give_zero":       {"en": "❌ Zero is useless.", "ru": "❌ Нулевое значение бесполезно."},
    "give_target_no":  {"en": "❌ Target not found.", "ru": "❌ Цель не найдена."},
    "give_to_all":     {"en": "✅ Given **{sign}{amount}** to all (`{n}` members)!", "ru": "✅ Выдано по **{sign}{amount}** всем (`{n}` членов)!"},
    "give_to_one":     {"en": "✅ Given **{sign}{amount}** to **{name}**", "ru": "✅ Выдано **{sign}{amount}** → **{name}**"},
    "give_to_role":    {"en": "✅ Given **{sign}{amount}** to role **{role}** (`{n}`)", "ru": "✅ Выдано по **{sign}{amount}** роли **{role}** (`{n}`)"},
    "give_currency":   {"en": "💰", "ru": "💰"},
    "give_xp_unit":    {"en": "XP", "ru": "XP"},
    "botprof_t":       {"en": "🎩 Don Core profile", "ru": "🎩 Профиль Don Core"},
    "botprof_name":    {"en": "New name (empty = keep)", "ru": "Новое имя (пусто = не менять)"},
    "botprof_name_ph": {"en": "2–32 characters", "ru": "2–32 символа"},
    "botprof_av":      {"en": "Avatar URL (empty = keep)", "ru": "URL аватарки (пусто = не менять)"},
    "botprof_av_ph":   {"en": "https://i.imgur.com/xxx.png", "ru": "https://i.imgur.com/xxx.png"},
    "botprof_nothing": {"en": "❌ Specify name or URL.", "ru": "❌ Укажи имя или URL."},
    "botprof_name_ok": {"en": "✅ Name → **{name}**", "ru": "✅ Имя → **{name}**"},
    "botprof_name_lim":{"en": "❌ Name: **Discord limit** — 2 per hour", "ru": "❌ Имя: **лимит Discord** — 2 раза в час"},
    "botprof_name_bad":{"en": "❌ Name: rejected by Discord", "ru": "❌ Имя: отклонено Discord"},
    "botprof_av_ok":   {"en": "✅ Avatar updated", "ru": "✅ Аватарка изменена"},
    "botprof_av_no":   {"en": "❌ Avatar: download failed ({code})", "ru": "❌ Аватар: не скачался ({code})"},
    "botprof_av_big":  {"en": "❌ Avatar: > 8 MB", "ru": "❌ Аватар: файл > 8 МБ"},
    "botprof_av_lim":  {"en": "❌ Avatar: limit — 2 per 10 min", "ru": "❌ Аватар: лимит — 2 раза в 10 минут"},
    "botprof_url_bad": {"en": "❌ Avatar: URL must start with http(s)://", "ru": "❌ Аватар: URL должен начинаться с http(s)://"},
    "botprof_log":     {"en": "Don Core profile changed", "ru": "Смена профиля Don Core"},
    "ab_t":            {"en": "🚨 Don's broadcast", "ru": "🚨 Рассылка Дона"},
    "ab_duration":     {"en": "Duration (sec)", "ru": "Длительность (сек)"},
    "ab_duration_ph":  {"en": "e.g. 20", "ru": "Например: 20"},
    "ab_pick_ch":      {"en": "👇 **{d} sec.** Choose channels:", "ru": "👇 **{d} сек.** Выберите каналы:"},
    "ab_pick_ph":      {"en": "Broadcast channels...", "ru": "Каналы для рассылки..."},
    "ab_no_ch":        {"en": "❌ Channels not found.", "ru": "❌ Каналы не определены."},
    "ab_start":        {"en": "🚀 **Don's broadcast started!** `{d} sec.`", "ru": "🚀 **Рассылка Дона запущена!** `{d} сек.`"},
    "ab_start_btn":    {"en": "START", "ru": "НАЧАТЬ"},
    "err_not_found":   {"en": "❌ Not found.", "ru": "❌ Не найдено."},
    "err_don_only":    {"en": "❌ Don only.", "ru": "❌ Только Дон."},
    "err_no_rights":   {"en": "❌ No rights.", "ru": "❌ Нет прав."},
    "err_bot":         {"en": "❌ Cannot target bots.", "ru": "❌ Ботам нельзя."},
    "err_self":        {"en": "❌ Cannot target yourself.", "ru": "❌ Себе нельзя."},
    "err_generic":     {"en": "❌ Errore. Try later.", "ru": "❌ Errore. Попробуйте позже."},
    "err_bad_id":      {"en": "❌ ID must contain only digits.", "ru": "❌ ID должен состоять только из цифр."},
    "err_user_no":     {"en": "❌ User not found.", "ru": "❌ Пользователь не найден."},
    "err_not_banned":  {"en": "❌ User is not banned.", "ru": "❌ Пользователь не в бан-листе."},
    "err_higher_role": {"en": "❌ Target has equal/higher role.", "ru": "❌ Роль цели выше или равна."},
    "err_bad_time":    {"en": "❌ Format: `30s`, `5m`, `1h`, `1d`. Min 10 sec.", "ru": "❌ Форматы: `30s`, `5m`, `1h`, `1d`. Мин 10 сек."},
    "err_max_28d":     {"en": "❌ Max 28 days.", "ru": "❌ Discord позволяет максимум 28 дней."},
    "err_max_7d":      {"en": "❌ Max 7 days.", "ru": "❌ Максимум 7 дней."},
    "err_admin_t":     {"en": "❌ Cannot target administrator.", "ru": "❌ Нельзя применить к администратору."},
    "poll_close":      {"en": "Close poll", "ru": "Закрыть опрос"},
    "poll_no_rights":  {"en": "❌ Only author or Don can close.", "ru": "❌ Только автор опроса или Дон."},
    "poll_results":    {"en": "🏁 Results", "ru": "🏁 Итоги"},
    "poll_none":       {"en": "no votes", "ru": "нет голосов"},
    "poll_winner":     {"en": "🏆 Winner", "ru": "🏆 Победитель"},
    "poll_author":     {"en": "Author", "ru": "Автор"},
    "rem_t":           {"en": "⏰ Reminder", "ru": "⏰ Напоминание"},
    "rem_what":        {"en": "What to remind?", "ru": "О чём напомнить?"},
    "rem_ph":          {"en": "e.g. family meeting", "ru": "Например: встреча семьи"},
    "rem_set":         {"en": "⏰ Will remind in **{dur}**: *{text}*", "ru": "⏰ Напомню через **{dur}**: *{text}*"},
    "rem_dm":          {"en": "⏰ **Reminder!**\n\n{text}\n\n*(set in {guild})*", "ru": "⏰ **Напоминание!**\n\n{text}\n\n*(установлено в {guild})*"},
    "rem_channel":     {"en": "⏰ {user}, reminder: **{text}**", "ru": "⏰ {user}, напоминание: **{text}**"},
    "bg_no_slot":      {"en": "❌ No background slot. Buy in `/shop` for 5000 💰.", "ru": "❌ У вас нет слота. Купите в `/shop` за 5000 💰."},
    "bg_url_bad":      {"en": "❌ URL must start with http:// or https://", "ru": "❌ Ссылка должна начинаться с http:// или https://"},
    "bg_ok":           {"en": "✅ **Fatto!** Profile background updated.", "ru": "✅ **Fatto!** Фон профиля обновлён."},
    "help_title":      {"en": "📚 {bot} commands", "ru": "📚 Команды {bot}"},
    "help_family":     {"en": "🎩 Family", "ru": "🎩 Семья"},
    "help_game":       {"en": "🔗 Game", "ru": "🔗 Игра"},
    "help_mod":        {"en": "🛡️ Moderation", "ru": "🛡️ Модерация"},
    "help_admin":      {"en": "⚙️ Don's controls", "ru": "⚙️ Управление Дона"},
    "help_footer":     {"en": "Type / to see commands", "ru": "Напиши / чтобы открыть команды"},
    "ach_top1":        {"en": "🥇 #1 of the family", "ru": "🥇 Топ-1 семьи"},
    "ach_top1_d":      {"en": "Take 1st place in /top by XP", "ru": "Занять 1 место в /top по XP"},
    "ach_rank5":       {"en": "🌟 Become Consigliere", "ru": "🌟 Стать Consigliere"},
    "ach_rank5_d":     {"en": "Reach rank 5 of the family", "ru": "Достичь 5-го ранга семьи"},
    "ach_jackpot":     {"en": "🎰 Jackpot x10", "ru": "🎰 Джекпот x10"},
    "ach_jackpot_d":   {"en": "Hit x10 in the casino", "ru": "Выбить x10 в казино"},
    "ach_verified":    {"en": "🔗 Verify Roblox", "ru": "🔗 Verifica Roblox"},
    "ach_verified_d":  {"en": "Complete /verify", "ru": "Пройти /verify"},
    "ach_rich":        {"en": "💰 Hoard 100 000", "ru": "💰 Накопить 100 000"},
    "ach_rich_d":      {"en": "Have 100k 💰 on balance", "ru": "Иметь 100k 💰 на балансе"},

    # --- ASK (МАГИЧЕСКИЙ ШАР) ---
    "ask_title": {"en": "🎩 The Don answers", "ru": "🎩 Дон отвечает"},
    "ask_question": {"en": "❓ Question", "ru": "❓ Вопрос"},
    "ask_yes": {"en": "✅ **Yes.**", "ru": "✅ **Да.**"},
    "ask_no": {"en": "❌ **No.**", "ru": "❌ **Нет.**"},
    "ask_maybe": {"en": "🤔 **Maybe.**", "ru": "🤔 **Возможно.**"},

    # --- STORY (ТЕКСТОВЫЙ КВЕСТ) ---
    "story_title": {"en": "🎩 Family Story", "ru": "🎩 История семьи"},
    "story_start": {"en": "You found a bag of money on the street. Take it?", "ru": "Ты нашёл сумку с деньгами на улице. Взять её себе?"},
    "story_keep": {"en": "You took the money. But a police car is passing by. Run?", "ru": "Ты взял деньги. Но тут проезжает полицейская машина. Побежать?"},
    "story_return": {"en": "You decided to return the bag. The owner turns out to be a mafioso and offers you a job. Accept?", "ru": "Ты решил вернуть сумку. Владелец оказался мафиози и предлагает тебе работу. Согласиться?"},
    "story_end_win_keep": {"en": "You hid in an alley and kept the money. The family is proud of you!", "ru": "Ты спрятался в переулке и сохранил деньги. Семья гордится тобой!"},
    "story_end_lose_keep": {"en": "The police noticed you. You are sent to jail.", "ru": "Полиция заметила тебя. Ты отправлен за решётку."},
    "story_end_win_return": {"en": "You became part of the family! Benvenuto.", "ru": "Ты стал частью семьи! Benvenuto."},
    "story_end_lose_return": {"en": "The owner was an undercover cop. Arrested.", "ru": "Владелец оказался полицейским под прикрытием. Арест."},
    "story_btn_yes": {"en": "Yes", "ru": "Да"},
    "story_btn_no": {"en": "No", "ru": "Нет"},

    # --- ПОКЕР (ПЕРЕВОДЫ) ---
    "pk_table_title": {"en": "🃏 Texas Hold'em — Don's Table", "ru": "🃏 Texas Hold'em — Стол Дона"},
    "pk_lobby_title": {"en": "🃏 Texas Hold'em — Lobby", "ru": "🃏 Texas Hold'em — лобби"},
    "pk_join_btn": {"en": "Join", "ru": "Присоединиться"},
    "pk_start_btn": {"en": "Start now", "ru": "Начать сейчас"},
    "pk_leave_btn": {"en": "Leave", "ru": "Выйти"},
    "pk_buyin": {"en": "💵 Buy-in", "ru": "💵 Бай-ин"},
    "pk_blinds": {"en": "🎯 Blinds", "ru": "🎯 Блайнды"},
    "pk_turn_time": {"en": "⏱ Turn time", "ru": "⏱ Время на ход"},
    "pk_players": {"en": "👥 Players", "ru": "👥 Игроков"},
    "pk_at_table": {"en": "**At the table:**", "ru": "**В столе:**"},
    "pk_need_more": {"en": "Need {} more. Host can start ▶️", "ru": "Нужно ещё {}. Хост может запустить ▶️"},
    "pk_host_start": {"en": "Host presses ▶️ to start", "ru": "Хост жмёт ▶️ для старта"},
    "pk_not_yours_game": {"en": "❌ Not your table.", "ru": "❌ Это не ваш стол."},
    "pk_your_hand": {"en": "🃏 Your hand", "ru": "🃏 Ваша рука"},
    "pk_cards": {"en": "🎩 Cards", "ru": "🎩 Карты"},
    "pk_stage": {"en": "📋 Table", "ru": "📋 Стол"},
    "pk_stack": {"en": "💵 Stack", "ru": "💵 Стек"},
    "pk_bet": {"en": "📥 Bet", "ru": "📥 Ставка"},
    "pk_to_call": {"en": "🎯 To call", "ru": "🎯 Доложить"},
    "pk_pot": {"en": "💰 Pot", "ru": "💰 Банк"},
    "pk_your_turn": {"en": "⏱ Your turn. Time: {} sec", "ru": "⏱ Ваш ход. Время: {} сек"},
    "pk_waiting_turn": {"en": "⏳ Waiting for opponent", "ru": "⏳ Ожидание чужого хода"},
    "pk_dealer": {"en": "🎴 **DEALER**", "ru": "🎴 **ДИЛЕР**"},
    "pk_dm_fail": {"en": "open DMs from the bot, otherwise you can't act (cards are not sent publicly).", "ru": "открой ЛС от бота — иначе не сможешь ходить (карты в публичный канал не отправляются)."},
    "pk_auto_fold": {"en": "⏰ <@{}> — **auto-fold**", "ru": "⏰ <@{}> — **авто-фолд**"},
    "pk_allin_showdown": {"en": "🔥 **Everyone ALL-IN — showdown!**", "ru": "🔥 **Все ALL-IN — вскрываем карты!**"},
    "pk_stage_bets": {"en": "🎴 **{}** — betting round", "ru": "🎴 **{}** — раунд ставок"},
    "pk_winner": {"en": "🏆 Winner", "ru": "🏆 Победитель"},
    "pk_wins_pot": {"en": "<@{}> takes the pot **{}** 💰\n*{}*", "ru": "<@{}> забирает банк **{}** 💰\n*{}*"},
    "pk_takes_pot": {"en": "<@{}> takes the pot", "ru": "<@{}> забирает банк"},
    "pk_split": {"en": "🤝 Pot split", "ru": "🤝 Банк разделён"},
    "pk_raised": {"en": "<@{}> — **Raised to {}**", "ru": "<@{}> — **Поднял до {}**"},
    "pk_folded": {"en": "<@{}> — **Fold**", "ru": "<@{}> — **Сброс**"},
    "pk_checked": {"en": "<@{}> — **Check**", "ru": "<@{}> — **Пропуск**"},
    "pk_called": {"en": "<@{}> — **Called {}**", "ru": "<@{}> — **Уравнял {}**"},
    "pk_allin": {"en": "<@{}> — **ALL-IN {}**", "ru": "<@{}> — **ВА-БАНК {}**"},
    "pk_closing": {"en": "💤 **Thread closes in 5 minutes.**", "ru": "💤 **Ветка закроется через 5 минут.**"},

    # --- БЛЭКДЖЕК (ПЕРЕВОДЫ) ---
    "bj_title": {"en": "🃏 Blackjack — vs Don Core", "ru": "🃏 Blackjack — vs Don Core"},
    "bj_result_title": {"en": "🃏 Blackjack — result", "ru": "🃏 Blackjack — итог"},
    "bj_your_cards": {"en": "🎩 Your cards", "ru": "🎩 Ваши карты"},
    "bj_dealer": {"en": "🤖 Dealer", "ru": "🤖 Дилер"},
    "bj_you": {"en": "🎩 You", "ru": "🎩 Вы"},
    "bj_sum": {"en": "sum", "ru": "сумма"},
    "bj_visible": {"en": "visible", "ru": "видно"},
    "bj_bet": {"en": "💰 Bet", "ru": "💰 Ставка"},
    "bj_bust": {"en": "💀 **BUST!** Lost: **-{}** 💰", "ru": "💀 **ПЕРЕБОР!** Потеряно: **-{}** 💰"},
    "bj_drew": {"en": "➕ Drew a card.", "ru": "➕ Взяли карту."},
    "bj_blackjack": {"en": "🌟 **BLACKJACK!** Won: **+{}** 💰", "ru": "🌟 **BLACKJACK!** Выигрыш: **+{}** 💰"},
    "bj_dealer_bj": {"en": "💀 **Dealer BLACKJACK.** Lost: **-{}** 💰", "ru": "💀 **У дилера BLACKJACK.** Потеряно: **-{}** 💰"},
    "bj_dealer_bust": {"en": "🎉 **Dealer busted!** Won: **+{}** 💰", "ru": "🎉 **Дилер перебрал!** Выигрыш: **+{}** 💰"},
    "bj_win": {"en": "🎉 **Victory!** Won: **+{}** 💰", "ru": "🎉 **Победа!** Выигрыш: **+{}** 💰"},
    "bj_lose": {"en": "💀 **Defeat.** Lost: **-{}** 💰", "ru": "💀 **Проигрыш.** Потеряно: **-{}** 💰"},
    "bj_draw": {"en": "🤝 **Draw.** Returned: **+{}** 💰", "ru": "🤝 **Ничья.** Возврат: **+{}** 💰"},
    "bj_both_bj": {"en": "🤝 Both have blackjack. Return.", "ru": "🤝 У обоих blackjack. Возврат."},
    "bj_bj_deal": {"en": "🌟 **BLACKJACK on deal!** Won: **+{}** 💰", "ru": "🌟 **BLACKJACK с раздачи!** Выигрыш: **+{}** 💰"},
    "bj_deal": {"en": "🎴 Cards dealt. Your turn.", "ru": "🎴 Карты раздали. Ход за вами."},
    "bj_not_yours": {"en": "❌ Not your game.", "ru": "❌ Это не ваша игра."},
    "bj_active": {"en": "❌ You already have an active game.", "ru": "❌ У вас уже активная игра."},
    "bj_need_coins": {"en": "❌ Need **{}** 💰, you have **{}** 💰.", "ru": "❌ Нужно **{}** 💰, у вас **{}** 💰."},
}


def tr(uid: int, gid: int | None, key: str, **kw) -> str:
    lang = ЯЗЫК_ПО_УМОЛЧАНИЮ
    if gid is not None:
        try:
            st = получить_статы(gid, uid)
            lang = st.get("lang", ЯЗЫК_ПО_УМОЛЧАНИЮ)
        except Exception:
            pass
    if lang not in ЯЗЫКИ:
        lang = ЯЗЫК_ПО_УМОЛЧАНИЮ
    row = СТРОКИ.get(key)
    if not row:
        return f"<{key}>"
    tmpl = row.get(lang) or row.get(ЯЗЫК_ПО_УМОЛЧАНИЮ) or f"<{key}>"
    try:
        return tmpl.format(**kw)
    except Exception:
        return tmpl


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("doncore")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.bans = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

_кд_казино: dict[tuple[int, int], float] = {}
_кд_перевода: dict[tuple[int, int], float] = {}
_история_сообщений: dict[tuple[int, int], deque] = defaultdict(
    lambda: deque(maxlen=ПОРОГ_СПАМА))
_нарушения: dict[tuple[int, int], dict] = {}
_инициализированные: set[int] = set()
_наказания: dict[int, dict[int, list]] = defaultdict(lambda: defaultdict(list))
_симуляция: dict[int, set] = defaultdict(set)


def выключено(gid: int, key: str) -> bool:
    s = _симуляция.get(gid, set())
    return key in s or "all" in s


def _профиль_юзера():
    return {
        "xp": 0, "coins": 100, "rank_override": 0,
        "lang": ЯЗЫК_ПО_УМОЛЧАНИЮ,
        "last_xp_time": 0, "last_msg_mission_time": 0,
        "streak_days": 0, "last_daily_time": 0, "last_reset_day": "",
        "missions": {
            "msg_count": 0, "media_count": 0, "casino_played": 0,
            "furry_triggered": 0, "claimed": [],
            "casino_wins": 0, "duel_wins": 0, "transfer_sent": 0,
            "shop_bought": 0, "poll_voted": 0, "roll_high": 0, "daily_claimed": 0,
        },
        "roblox_id": None, "roblox_username": None, "verified": False,
        "verify_code": None, "verify_code_expires": 0,
        "titles": [], "inventory": [], "profile_bg": None,
        "achievements": [],
        "total_casino_jackpots": 0,
    }


def _настройки_сервера():
    return {
        "target": None, "emojis": [], "changelog": [], "bugs": {}, "suggestions": {},
        "automod_enabled": True, "bad_words": list(ПЛОХИЕ_СЛОВА),
        "bot_logs_protect": True,
    }


def загрузить_данные():
    if os.path.exists(ФАЙЛ_ДАННЫХ):
        try:
            with open(ФАЙЛ_ДАННЫХ, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {int(g): {int(u): d for u, d in users.items()}
                    for g, users in raw.items()}
        except Exception as e:
            log.error(f"Ошибка загрузки данных: {e}")
    return {}


def загрузить_настройки():
    if os.path.exists(ФАЙЛ_НАСТРОЕК):
        try:
            with open(ФАЙЛ_НАСТРОЕК, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {int(g): {**_настройки_сервера(), **s} for g, s in raw.items()}
        except Exception as e:
            log.error(f"Ошибка загрузки настроек: {e}")
    return {}


def загрузить_наказания():
    if os.path.exists(ФАЙЛ_НАКАЗАНИЙ):
        try:
            with open(ФАЙЛ_НАКАЗАНИЙ, "r", encoding="utf-8") as f:
                raw = json.load(f)
            d = defaultdict(lambda: defaultdict(list))
            for g, users in raw.items():
                for u, recs in users.items():
                    d[int(g)][int(u)] = recs
            return d
        except Exception as e:
            log.error(f"Ошибка загрузки наказаний: {e}")
    return defaultdict(lambda: defaultdict(list))


данные_юзеров = загрузить_данные()
настройки_серверов = загрузить_настройки()
_наказания = загрузить_наказания()


def сохранить_данные():
    try:
        with open(ФАЙЛ_ДАННЫХ, "w", encoding="utf-8") as f:
            json.dump(данные_юзеров, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log.error(f"Ошибка сохранения данных: {e}")


def сохранить_настройки():
    try:
        with open(ФАЙЛ_НАСТРОЕК, "w", encoding="utf-8") as f:
            json.dump(настройки_серверов, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log.error(f"Ошибка сохранения настроек: {e}")


def сохранить_наказания():
    try:
        out = {}
        for g, users in _наказания.items():
            out[str(g)] = {}
            for u, recs in users.items():
                out[str(g)][str(u)] = recs
        with open(ФАЙЛ_НАКАЗАНИЙ, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log.error(f"Ошибка сохранения наказаний: {e}")


def добавить_наказание(gid: int, uid: int, тип: str, причина: str,
                       мод_id: int, **extra):
    rec = {"type": тип, "reason": причина, "mod_id": мод_id,
           "ts": time.time(), **extra}
    _наказания[gid][uid].append(rec)
    сохранить_наказания()


def получить_настройки(gid: int) -> dict:
    if gid not in настройки_серверов:
        настройки_серверов[gid] = _настройки_сервера()
    else:
        for k, v in _настройки_сервера().items():
            настройки_серверов[gid].setdefault(k, v)
    return настройки_серверов[gid]


def _сегодня_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def получить_статы(gid: int, uid: int) -> dict:
    if gid not in данные_юзеров:
        данные_юзеров[gid] = {}
    if uid not in данные_юзеров[gid]:
        данные_юзеров[gid][uid] = _профиль_юзера()
        return данные_юзеров[gid][uid]

    rec = данные_юзеров[gid][uid]
    d = _профиль_юзера()
    for k, v in d.items():
        if k not in rec:
            rec[k] = v

    if not isinstance(rec.get("missions"), dict):
        rec["missions"] = d["missions"]
    else:
        for k, v in d["missions"].items():
            rec["missions"].setdefault(k, v)
        if not isinstance(rec["missions"].get("claimed"), list):
            rec["missions"]["claimed"] = []

    for lk in ["titles", "inventory", "achievements"]:
        if not isinstance(rec.get(lk), list):
            rec[lk] = []
    return rec


def сбросить_миссии(stats: dict) -> bool:
    today = _сегодня_utc()
    if stats.get("last_reset_day") != today:
        stats["last_reset_day"] = today
        stats["missions"] = {
            "msg_count": 0, "media_count": 0, "casino_played": 0,
            "furry_triggered": 0, "claimed": [],
            "casino_wins": 0, "duel_wins": 0, "transfer_sent": 0,
            "shop_bought": 0, "poll_voted": 0, "roll_high": 0, "daily_claimed": 0,
        }
        return True
    return False


def прогресс_бар(p: float, length: int = 12) -> str:
    p = max(0.0, min(1.0, p))
    n = int(round(p * length))
    return "█" * n + "░" * (length - n)


def парсить_время(s: str) -> int | None:
    m = re.match(r"^(\d+)\s*([smhd])$", s.lower().strip())
    if not m:
        return None
    n = int(m.group(1)); u = m.group(2)
    return n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]


def человеческое_время(sec: int) -> str:
    if sec < 60: return f"{sec}s"
    if sec < 3600: return f"{sec // 60}m"
    if sec < 86400: return f"{sec // 3600}h"
    return f"{sec // 86400}d"


def _нормализовать(name: str) -> str:
    return "".join(c for c in name.lower() if c.isascii() and (c.isalnum() or c in "-_"))


def найти_канал(guild: discord.Guild, base: str) -> discord.TextChannel | None:
    b = base.lower()
    for ch in guild.text_channels:
        if ch.name.lower() == b:
            return ch
    for ch in guild.text_channels:
        c = _нормализовать(ch.name)
        if c == b or c.endswith(b):
            return ch
    return None


def найти_роль(guild: discord.Guild, base: str) -> discord.Role | None:
    b = base.lower()
    for r in guild.roles:
        if r.name.lower() == b:
            return r
    bc = _нормализовать(base)
    for r in guild.roles:
        if _нормализовать(r.name) == bc:
            return r
    for r in guild.roles:
        if _нормализовать(r.name).endswith(bc):
            return r
    return None


async def в_лог(guild: discord.Guild, embed: discord.Embed):
    ch = найти_канал(guild, КАНАЛ_ЛОГОВ)
    if not ch:
        return
    try:
        await ch.send(embed=embed)
    except Exception as e:
        log.warning(f"Не отправилось в лог: {e}")


async def лог_админа(guild, admin: discord.Member, action: str, details: str):
    embed = discord.Embed(
        title=f"🎩 {action}", description=details,
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc))
    embed.set_footer(text=f"Don: {admin.display_name}",
                     icon_url=admin.display_avatar.url)
    await в_лог(guild, embed)


async def выдать_достижение(guild: discord.Guild, uid: int, key: str):
    if key not in ДОСТИЖЕНИЯ:
        return
    stats = получить_статы(guild.id, uid)
    if key in stats.get("achievements", []):
        return
    ach = ДОСТИЖЕНИЯ[key]
    stats.setdefault("achievements", []).append(key)
    stats["xp"] += ach["xp"]
    сохранить_данные()

    member = guild.get_member(uid)
    if member:
        asyncio.create_task(проверить_роли(member, stats["xp"], stats["rank_override"]))

    name = tr(uid, guild.id, ach["name_key"])
    desc = tr(uid, guild.id, ach["desc_key"])

    embed = discord.Embed(
        title=tr(uid, guild.id, "ach_new"),
        description=(f"{name}\n\n"
                     f"**{tr(uid, guild.id, 'ach_member')}:** <@{uid}>\n"
                     f"**{tr(uid, guild.id, 'ach_reward')}:** `+{ach['xp']} XP`"),
        color=discord.Color.gold(),
        timestamp=datetime.now(timezone.utc))
    await в_лог(guild, embed)

    if member:
        try:
            await member.send(tr(uid, guild.id, "ach_dm", name=name, desc=desc, xp=ach["xp"]))
        except Exception:
            pass


def рассчитать_ранг(xp: int, override: int = 0):
    if override > 0:
        if override == 6:
            return 6, 1.0, ОТОБРАЖЕНИЕ_РАНГОВ[6]
        stars = min(override, 5)
        prev = 0 if stars == 1 else ПОРОГИ_XP[stars - 2]
        nxt = ПОРОГИ_XP[stars - 1]
        cur = max(0, xp - prev)
        need = nxt - prev
        prog = min(1.0, cur / need) if need > 0 else 1.0
        return stars, prog, ОТОБРАЖЕНИЕ_РАНГОВ.get(stars, "?")
    stars = 0
    for i, t in enumerate(ПОРОГИ_XP):
        if xp >= t:
            stars = i + 1
        else:
            break
    if stars >= 5:
        prog = 1.0
    else:
        prev = 0 if stars == 0 else ПОРОГИ_XP[stars - 1]
        nxt = ПОРОГИ_XP[stars]
        cur = xp - prev
        need = nxt - prev
        prog = cur / need if need > 0 else 0
    return stars, prog, ОТОБРАЖЕНИЕ_РАНГОВ.get(stars, "?")


def эмбед_профиля(stats: dict, member: discord.Member) -> discord.Embed:
    stars, prog, rname = рассчитать_ранг(stats["xp"], stats["rank_override"])
    color = ЦВЕТА_РАНГОВ.get(stars, discord.Color.dark_gold())
    uid = member.id; gid = member.guild.id

    if stars == 6:
        visual = "🎩🎩🎩🎩🎩"
        next_line = "\n" + tr(uid, gid, "prof_max")
    else:
        visual = f"`{прогресс_бар(prog, 12)}` **{int(prog * 100)}%**"
        if stars < 5:
            nx = ПОРОГИ_XP[stars]
            rem = max(0, nx - stats["xp"])
            next_line = "\n" + tr(uid, gid, "prof_until_next", xp=rem)
        else:
            next_line = "\n" + tr(uid, gid, "prof_max")

    extra = ""
    titles = stats.get("titles", [])
    if titles:
        extra += "\n" + tr(uid, gid, "prof_title_l", title=titles[-1])
    if stats.get("verified"):
        extra += "\n" + tr(uid, gid, "prof_roblox", nick=stats["roblox_username"])
    ach_n = len(stats.get("achievements", []))
    extra += "\n" + tr(uid, gid, "prof_ach", have=ach_n, total=len(ДОСТИЖЕНИЯ))

    embed = discord.Embed(
        title=tr(uid, gid, "prof_title", name=member.display_name),
        description=(tr(uid, gid, "prof_xp_money", xp=stats["xp"], coins=stats["coins"])
                     + "\n" + tr(uid, gid, "prof_rank", rank=rname)
                     + f"\n\n{visual}{next_line}{extra}"),
        color=color,
        timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"ID: {member.id}")
    if stats.get("profile_bg"):
        embed.set_image(url=stats["profile_bg"])
    return embed


async def создать_роли(guild: discord.Guild):
    created = 0
    for name in ВСЕ_РОЛИ_БОТА:
        if найти_роль(guild, name):
            continue
        try:
            await guild.create_role(name=name, reason="DonCore: автосоздание")
            created += 1
            log.info(f"Создана роль '{name}' на {guild.name}")
        except discord.Forbidden:
            log.warning(f"Нет прав создать роль '{name}'")
        except Exception as e:
            log.error(f"Ошибка создания роли '{name}': {e}")
    if created == 0:
        log.info(f"Все роли уже есть на {guild.name}")


async def проверить_роли(member: discord.Member, xp: int, override: int = 0):
    if member.bot:
        return
    guild = member.guild

    if выключено(guild.id, "rank_roles"):
        return

    stars, _, _ = рассчитать_ранг(xp, override)
    if stars >= 6:
        return
    tname = ИМЕНА_РОЛЕЙ.get(stars)
    trole = найти_роль(guild, tname) if tname else None

    for rn in ИМЕНА_РОЛЕЙ.values():
        r = найти_роль(guild, rn)
        if r and r in member.roles and r != trole:
            try:
                await member.remove_roles(r, reason="DonCore: смена ранга")
            except Exception as e:
                log.warning(f"Не снял роль {r.name}: {e}")

    if trole and trole not in member.roles:
        try:
            await member.add_roles(trole, reason="DonCore: новый ранг")
            if stars == 5:
                asyncio.create_task(выдать_достижение(guild, member.id, "rank5"))
        except Exception as e:
            log.warning(f"Не выдал роль {trole.name}: {e}")


def в_белом_списке(member: discord.Member) -> bool:
    if member.bot: return True
    if member.guild_permissions.administrator: return True
    if member.guild_permissions.manage_messages: return True
    return False


def содержит_мат(text: str, words: list[str]) -> str | None:
    t = text.lower()
    tc = re.sub(r"[^\w\s]", "", t)
    for w in words:
        if w in tc:
            return w
    return None


def это_спам(gid: int, uid: int, content: str) -> bool:
    key = (gid, uid)
    now = time.time()
    h = _история_сообщений[key]
    h.append((content.lower().strip(), now))
    while h and now - h[0][1] > ОКНО_СПАМА:
        h.popleft()
    if len(h) < ПОРОГ_СПАМА:
        return False
    first = h[0][0]
    if not first:
        return False
    return all(m[0] == first for m in h)


def состояние_нарушения(gid: int, uid: int) -> dict:
    key = (gid, uid)
    today = _сегодня_utc()
    st = _нарушения.get(key)
    if not st or st.get("date") != today:
        st = {"date": today, "count": 0}
        _нарушения[key] = st
    return st


async def обработать_нарушение(message: discord.Message, reason_key: str, **kw):
    guild = message.guild
    member = message.author
    try:
        await message.delete()
    except Exception:
        pass

    st = состояние_нарушения(guild.id, member.id)
    st["count"] += 1

    reason = tr(member.id, guild.id, reason_key, **kw)

    embed = discord.Embed(
        title=tr(member.id, guild.id, "am_violation_t"),
        description=(f"**{tr(member.id, guild.id, 'am_who')}:** {member.mention} (`{member.id}`)\n"
                     f"**{tr(member.id, guild.id, 'am_where')}:** {message.channel.mention}\n"
                     f"**{tr(member.id, guild.id, 'am_reason')}:** {reason}\n"
                     f"**{tr(member.id, guild.id, 'am_nth', n=st['count'])}**"),
        color=discord.Color.dark_red(),
        timestamp=datetime.now(timezone.utc))

    if st["count"] == 1:
        try:
            await message.channel.send(
                tr(member.id, guild.id, "am_warn",
                   user=member.mention, reason=reason, h=ЧАСОВ_МУТА),
                delete_after=15)
        except Exception:
            pass
        embed.set_footer(text=tr(member.id, guild.id, "am_action_warn"))
        добавить_наказание(guild.id, member.id, "warn", f"[Auto] {reason}",
                           bot.user.id if bot.user else 0)
    else:
        try:
            await member.timeout_for(timedelta(hours=ЧАСОВ_МУТА),
                                     reason=f"DonCore automod: {reason}")
            try:
                await message.channel.send(
                    tr(member.id, guild.id, "am_mute", user=member.mention, h=ЧАСОВ_МУТА),
                    delete_after=15)
            except Exception:
                pass
            embed.set_footer(text=tr(member.id, guild.id, "am_action_mute", h=ЧАСОВ_МУТА))
            добавить_наказание(guild.id, member.id, "mute", f"[Auto] {reason}",
                               bot.user.id if bot.user else 0,
                               duration=ЧАСОВ_МУТА * 3600)
        except Exception as e:
            log.warning(f"Не замутил {member}: {e}")
            embed.set_footer(text=tr(member.id, guild.id, "am_cant_mute"))
    await в_лог(guild, embed)


async def проверить_автомод(message: discord.Message) -> bool:
    s = получить_настройки(message.guild.id)
    if not s.get("automod_enabled", True): return False
    if выключено(message.guild.id, "automod"): return False
    if not message.guild or message.author.bot: return False
    if в_белом_списке(message.author): return False

    words = s.get("bad_words", ПЛОХИЕ_СЛОВА)
    bad = содержит_мат(message.content, words)
    if bad:
        await обработать_нарушение(message, "am_reason", reason=f"`{bad}`")
        return True

    if это_спам(message.guild.id, message.author.id, message.content):
        await обработать_нарушение(message, "am_reason",
                                   reason=f"spam (≥{ПОРОГ_СПАМА})")
        return True

    if not message.author.guild_permissions.mention_everyone:
        lc = message.content.lower()
        if message.mention_everyone or "@everyone" in lc or "@here" in lc:
            await обработать_нарушение(message, "am_reason",
                                       reason="@everyone/@here без прав")
            return True
    return False


async def защита_лог_канала(message: discord.Message) -> bool:
    if not message.guild: return False
    s = получить_настройки(message.guild.id)
    if not s.get("bot_logs_protect", True): return False

    ch = найти_канал(message.guild, КАНАЛ_ЛОГОВ)
    if not ch or message.channel.id != ch.id: return False
    if bot.user and message.author.id == bot.user.id: return False
    if message.webhook_id: return False

    try:
        await message.delete()
    except Exception:
        return False

    try:
        await message.channel.send(
            tr(message.author.id, message.guild.id, "botlog_protect",
               user=message.author.mention), delete_after=10)
    except Exception:
        pass
    return True


async def roblox_по_нику(username: str) -> dict | None:
    url = f"{ROBLOX_API}/usernames/users"
    payload = {"usernames": [username], "excludeBannedUsers": True}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, json=payload,
                              timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200: return None
                d = await r.json()
                u = d.get("data", [])
                return u[0] if u else None
    except Exception as e:
        log.error(f"Roblox API: {e}")
        return None


async def roblox_описание(uid: int) -> str | None:
    url = f"{ROBLOX_API}/users/{uid}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200: return None
                d = await r.json()
                return d.get("description", "")
    except Exception as e:
        log.error(f"Roblox API: {e}")
        return None


def сгенерировать_код() -> str:
    a = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ПРЕФИКС_КОДА + "".join(random.choice(a) for _ in range(5))


def кд_казино_ок(gid: int, uid: int) -> float:
    key = (gid, uid); now = time.time()
    last = _кд_казино.get(key, 0)
    rem = КД_КАЗИНО - (now - last)
    if rem <= 0:
        _кд_казино[key] = now
        return 0
    return rem


def кд_перевода_ок(gid: int, uid: int) -> float:
    key = (gid, uid); now = time.time()
    last = _кд_перевода.get(key, 0)
    rem = КД_ПЕРЕВОДА - (now - last)
    if rem <= 0:
        _кд_перевода[key] = now
        return 0
    return rem


# ============================================================
# ПОКЕР — ГЛОБАЛЬНЫЕ ХРАНИЛИЩА
# ============================================================
_покер_толы: dict[int, dict] = {}
_покер_таймеры: dict[int, asyncio.Task] = {}

_ПК_МАСТИ = ["♠️", "♥️", "♦️", "♣️"]
_ПК_СИМВ = {14:"A",13:"K",12:"Q",11:"J",10:"10",9:"9",8:"8",7:"7",
            6:"6",5:"5",4:"4",3:"3",2:"2"}


def _покер_сохранить():
    try:
        out = {}
        for mid, s in _покер_толы.items():
            copy = {k: v for k, v in s.items() if k not in ("interaction", "view_ephemeral")}
            copy["folded"] = list(copy.get("folded", []))
            copy["all_in"] = list(copy.get("all_in", []))
            copy["acted"] = list(copy.get("acted", set()))
            out[str(mid)] = copy
        with open(ФАЙЛ_ПОКЕРА, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
    except Exception as e:
        log.error(f"Ошибка сохранения покера: {e}")


def _покер_загрузить():
    if not os.path.exists(ФАЙЛ_ПОКЕРА):
        return {}
    try:
        with open(ФАЙЛ_ПОКЕРА, "r", encoding="utf-8") as f:
            raw = json.load(f)
        out = {}
        for k, s in raw.items():
            s["folded"] = set(s.get("folded", []))
            s["all_in"] = set(s.get("all_in", []))
            s.setdefault("acted", set())
            if isinstance(s["acted"], list):
                s["acted"] = set(s["acted"])

            использованные = set()
            for uid_cards in s.get("hole", {}).values():
                for c in uid_cards:
                    использованные.add(tuple(c) if isinstance(c, list) else c)
            for c in s.get("community", []):
                использованные.add(tuple(c) if isinstance(c, list) else c)

            deck = s.get("deck", [])
            нов_дек = []
            for c in deck:
                cc = tuple(c) if isinstance(c, list) else c
                if cc not in использованные:
                    нов_дек.append(c)
                    использованные.add(cc)
            s["deck"] = нов_дек

            out[int(k)] = s
        return out
    except Exception as e:
        log.error(f"Ошибка загрузки покера: {e}")
        return {}


# ============================================================
# КНОПКА ЗАКРЫТИЯ
# ============================================================
class КнопкаЗакрыть(Button):
    def __init__(self, uid: int, gid: int, row: int = 4):
        super().__init__(label=tr(uid, gid, "close_btn"),
                         style=discord.ButtonStyle.secondary,
                         emoji="❌", row=row)
        self.uid = uid
        self.gid = gid

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception:
            await interaction.response.send_message("❌", ephemeral=True)


# ============================================================
# ИГРА STORY
# ============================================================
class StoryView(View):
    def __init__(self, uid, gid, stage="start"):
        super().__init__(timeout=60)
        self.uid = uid
        self.gid = gid
        self.stage = stage

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, emoji="✅")
    async def btn_yes(self, button, interaction):
        if interaction.user.id != self.uid:
            await interaction.response.send_message("❌ Not your game.", ephemeral=True); return
        
        gid = self.gid; uid = self.uid
        if self.stage == "start":
            text = tr(uid, gid, "story_keep")
            await interaction.response.edit_message(content=text, view=StoryView(uid, gid, "keep"))
        elif self.stage == "keep":
            text = tr(uid, gid, "story_end_win_keep") + "\n\n🎉 **+500 💰**"
            st = получить_статы(gid, uid)
            st["coins"] += 500
            сохранить_данные()
            await interaction.response.edit_message(content=text, view=None)
        elif self.stage == "return":
            text = tr(uid, gid, "story_end_win_return") + "\n\n🎉 **+1000 💰**"
            st = получить_статы(gid, uid)
            st["coins"] += 1000
            сохранить_данные()
            await interaction.response.edit_message(content=text, view=None)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, emoji="❌")
    async def btn_no(self, button, interaction):
        if interaction.user.id != self.uid:
            await interaction.response.send_message("❌ Not your game.", ephemeral=True); return
            
        gid = self.gid; uid = self.uid
        if self.stage == "start":
            text = tr(uid, gid, "story_return")
            await interaction.response.edit_message(content=text, view=StoryView(uid, gid, "return"))
        elif self.stage == "keep":
            text = tr(uid, gid, "story_end_lose_keep")
            await interaction.response.edit_message(content=text, view=None)
        elif self.stage == "return":
            text = tr(uid, gid, "story_end_lose_return")
            await interaction.response.edit_message(content=text, view=None)


# ============================================================
# МОДАЛКИ АДМИНА
# ============================================================
class МодалкаПароль(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "adm_pass_title"))
        self.add_item(InputText(
            label=tr(uid, gid, "adm_pass_label"),
            placeholder=tr(uid, gid, "adm_pass_ph"),
            style=discord.InputTextStyle.short, required=True))

    async def callback(self, interaction: discord.Interaction):
        if self.children[0].value != ADMIN_PASSWORD:
            await interaction.response.send_message(
                tr(interaction.user.id, interaction.guild.id, "adm_wrong_pass"),
                ephemeral=True)
            return
        await interaction.response.send_message(
            tr(interaction.user.id, interaction.guild.id, "adm_welcome"),
            view=АдминПанель(interaction.guild), ephemeral=True)


class МодалкаРеакций(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "react_title"))
        self.add_item(InputText(label=tr(uid, gid, "react_who"),
                                placeholder=tr(uid, gid, "react_who_ph"),
                                style=discord.InputTextStyle.short, required=True))
        self.add_item(InputText(label=tr(uid, gid, "react_emojis"),
                                placeholder=tr(uid, gid, "react_emojis_ph"),
                                style=discord.InputTextStyle.short, required=True))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        target = self.children[0].value.strip()
        emojis = self.children[1].value.strip().split()
        if not emojis:
            await interaction.response.send_message(tr(uid, gid, "react_no_emoji"),
                                                    ephemeral=True)
            return
        if target.startswith("<@") and target.endswith(">"):
            target = target.strip("<@!>")
        s = получить_настройки(gid)
        s["target"] = target
        s["emojis"] = emojis
        сохранить_настройки()
        await лог_админа(interaction.guild, interaction.user, "Auto-reactions",
                         f"Target: `{target}`\nEmojis: `{' '.join(emojis)}`")
        await interaction.response.send_message(
            tr(uid, gid, "react_saved", target=target, emojis=' '.join(emojis)),
            ephemeral=True)


class МодалкаВыдатьДеньги(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "give_coins_t"))
        self.add_item(InputText(label=tr(uid, gid, "give_who"),
                                placeholder=tr(uid, gid, "give_who_ph"),
                                style=discord.InputTextStyle.short, required=True))
        self.add_item(InputText(label=tr(uid, gid, "give_amount"),
                                placeholder=tr(uid, gid, "give_amount_ph"),
                                style=discord.InputTextStyle.short, required=True))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        q = self.children[0].value.strip()
        try:
            amount = int(self.children[1].value.strip())
        except ValueError:
            await interaction.response.send_message(tr(uid, gid, "give_number"),
                                                    ephemeral=True)
            return
        if amount <= 0:
            await interaction.response.send_message(tr(uid, gid, "give_positive"),
                                                    ephemeral=True)
            return
        n = 0
        if q.lower() in ("all", "все"):
            данные_юзеров.setdefault(gid, {})
            for m in interaction.guild.members:
                if not m.bot:
                    получить_статы(gid, m.id)["coins"] += amount
                    n += 1
            сохранить_данные()
            await лог_админа(interaction.guild, interaction.user, "Give money",
                             f"All: **+{amount}** 💰 (`{n}`)")
            await interaction.response.send_message(
                tr(uid, gid, "give_to_all", sign="+", amount=amount, n=n),
                ephemeral=True)
            return
        if q.isdigit():
            tuid = int(q)
            получить_статы(gid, tuid)["coins"] += amount
            сохранить_данные()
            m = interaction.guild.get_member(tuid)
            name = m.name if m else f"ID: {tuid}"
            await лог_админа(interaction.guild, interaction.user, "Give money",
                             f"{name} (`{tuid}`): **+{amount}** 💰")
            await interaction.response.send_message(
                tr(uid, gid, "give_to_one", sign="+", amount=amount, name=name),
                ephemeral=True)
            return
        role = discord.utils.get(interaction.guild.roles, name=q)
        if role:
            for m in interaction.guild.members:
                if not m.bot and role in m.roles:
                    получить_статы(gid, m.id)["coins"] += amount
                    n += 1
            сохранить_данные()
            await лог_админа(interaction.guild, interaction.user, "Give money",
                             f"Role `{role.name}`: **+{amount}** 💰 (`{n}`)")
            await interaction.response.send_message(
                tr(uid, gid, "give_to_role", sign="+", amount=amount,
                   role=role.name, n=n), ephemeral=True)
        else:
            await interaction.response.send_message(tr(uid, gid, "give_target_no"),
                                                    ephemeral=True)


class МодалкаВыдатьXP(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "give_xp_t"))
        self.add_item(InputText(label=tr(uid, gid, "give_who"),
                                placeholder=tr(uid, gid, "give_who_ph"),
                                style=discord.InputTextStyle.short, required=True))
        self.add_item(InputText(label=tr(uid, gid, "give_amount"),
                                placeholder=tr(uid, gid, "give_amount_ph"),
                                style=discord.InputTextStyle.short, required=True))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        q = self.children[0].value.strip()
        try:
            amount = int(self.children[1].value.strip())
        except ValueError:
            await interaction.response.send_message(tr(uid, gid, "give_number"),
                                                    ephemeral=True)
            return
        if amount == 0:
            await interaction.response.send_message(tr(uid, gid, "give_zero"),
                                                    ephemeral=True)
            return
        sign = "+" if amount > 0 else ""
        n = 0
        if q.lower() in ("all", "все"):
            данные_юзеров.setdefault(gid, {})
            for m in interaction.guild.members:
                if not m.bot:
                    st = получить_статы(gid, m.id)
                    st["xp"] = max(0, st["xp"] + amount)
                    n += 1
                    asyncio.create_task(проверить_роли(m, st["xp"], st["rank_override"]))
            сохранить_данные()
            await лог_админа(interaction.guild, interaction.user, "Give XP",
                             f"All: **{sign}{amount}** XP (`{n}`)")
            await interaction.response.send_message(
                tr(uid, gid, "give_to_all", sign=sign, amount=amount, n=n),
                ephemeral=True)
            return
        if q.isdigit():
            tuid = int(q)
            st = получить_статы(gid, tuid)
            st["xp"] = max(0, st["xp"] + amount)
            сохранить_данные()
            m = interaction.guild.get_member(tuid)
            name = m.name if m else f"ID: {tuid}"
            if m:
                asyncio.create_task(проверить_роли(m, st["xp"], st["rank_override"]))
            await лог_админа(interaction.guild, interaction.user, "Give XP",
                             f"{name}: **{sign}{amount}** XP")
            await interaction.response.send_message(
                tr(uid, gid, "give_to_one", sign=sign, amount=amount, name=name),
                ephemeral=True)
            return
        role = discord.utils.get(interaction.guild.roles, name=q)
        if role:
            for m in interaction.guild.members:
                if not m.bot and role in m.roles:
                    st = получить_статы(gid, m.id)
                    st["xp"] = max(0, st["xp"] + amount)
                    n += 1
                    asyncio.create_task(проверить_роли(m, st["xp"], st["rank_override"]))
            сохранить_данные()
            await лог_админа(interaction.guild, interaction.user, "Give XP",
                             f"Role `{role.name}`: **{sign}{amount}** XP (`{n}`)")
            await interaction.response.send_message(
                tr(uid, gid, "give_to_role", sign=sign, amount=amount,
                   role=role.name, n=n), ephemeral=True)
        else:
            await interaction.response.send_message(tr(uid, gid, "give_target_no"),
                                                    ephemeral=True)


class МодалкаПрофильБота(Modal):
    def __init__(self, bot_, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "botprof_t"))
        self.bot_ = bot_
        self.add_item(InputText(
            label=tr(uid, gid, "botprof_name"),
            placeholder=tr(uid, gid, "botprof_name_ph"),
            style=discord.InputTextStyle.short, required=False, max_length=32))
        self.add_item(InputText(
            label=tr(uid, gid, "botprof_av"),
            placeholder=tr(uid, gid, "botprof_av_ph"),
            style=discord.InputTextStyle.short, required=False))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        new_name = self.children[0].value.strip()
        avatar_url = self.children[1].value.strip()

        if not new_name and not avatar_url:
            await interaction.response.send_message(tr(uid, gid, "botprof_nothing"),
                                                    ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        results = []

        if new_name:
            try:
                await self.bot_.user.edit(username=new_name)
                results.append(tr(uid, gid, "botprof_name_ok", name=new_name))
            except discord.HTTPException as e:
                if e.status == 429:
                    results.append(tr(uid, gid, "botprof_name_lim"))
                elif e.status == 400:
                    results.append(tr(uid, gid, "botprof_name_bad"))
                else:
                    results.append(f"❌ {e.status}")
            except Exception as e:
                results.append(f"❌ {e}")

        if avatar_url:
            if not avatar_url.startswith("http"):
                results.append(tr(uid, gid, "botprof_url_bad"))
            else:
                try:
                    async with aiohttp.ClientSession() as ss:
                        async with ss.get(avatar_url,
                                          timeout=aiohttp.ClientTimeout(total=15)) as rr:
                            if rr.status != 200:
                                results.append(tr(uid, gid, "botprof_av_no",
                                                  code=rr.status))
                            else:
                                data = await rr.read()
                                if len(data) > 8 * 1024 * 1024:
                                    results.append(tr(uid, gid, "botprof_av_big"))
                                else:
                                    await self.bot_.user.edit(avatar=data)
                                    results.append(tr(uid, gid, "botprof_av_ok"))
                except discord.HTTPException as e:
                    if e.status == 429:
                        results.append(tr(uid, gid, "botprof_av_lim"))
                    else:
                        results.append(f"❌ {e.status}")
                except Exception as e:
                    results.append(f"❌ {e}")

        await interaction.followup.send("\n".join(results), ephemeral=True)

        details = []
        if new_name: details.append(f"Name → `{new_name}`")
        if avatar_url: details.append(f"Avatar: `{avatar_url[:80]}`")
        await лог_админа(interaction.guild, interaction.user,
                         tr(uid, gid, "botprof_log"), "\n".join(details))


class МодалкаРассылки(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "ab_t"))
        self.add_item(InputText(
            label=tr(uid, gid, "ab_duration"),
            placeholder=tr(uid, gid, "ab_duration_ph"),
            style=discord.InputTextStyle.short, required=True, value="20"))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        try:
            dur = max(1, min(300, int(self.children[0].value.strip())))
        except ValueError:
            dur = 20
        await interaction.response.edit_message(
            content=tr(uid, gid, "ab_pick_ch", d=dur),
            view=ВыборКаналовРассылки(dur, uid, gid))


class ВыборКаналовРассылки(View):
    def __init__(self, dur: int, uid: int, gid: int):
        super().__init__(timeout=180)
        self.dur = dur; self.uid = uid; self.gid = gid
        sel = discord.ui.ChannelSelect(
            placeholder=tr(uid, gid, "ab_pick_ph"),
            min_values=1, max_values=5,
            channel_types=[discord.ChannelType.text])
        sel.callback = self._on_pick
        self.add_item(sel)

    async def _on_pick(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        raw = interaction.data.get("values") or []
        resolved = []
        for v in raw:
            cid = int(v) if isinstance(v, (str, int)) else v.id
            ch = interaction.guild.get_channel(cid)
            if ch: resolved.append(ch)
        if not resolved:
            await interaction.response.send_message(tr(uid, gid, "ab_no_ch"),
                                                    ephemeral=True)
            return
        await interaction.response.send_message(
            tr(uid, gid, "ab_start", d=self.dur), ephemeral=True)
        await лог_админа(interaction.guild, interaction.user, "Don broadcast",
                         f"Channels: {', '.join(c.mention for c in resolved)}\n`{self.dur} sec.`")

        lines = [
            "🎩 Don Core передаёт слово семье...",
            "Non si tocca la famiglia.",
            "La famiglia è tutto.",
            "Ricorda il tuo posto, Soldato.",
            "Il Don vede tutto.",
            "Silenzio, amico mio.",
        ]
        start = time.time()
        while time.time() - start < self.dur:
            for line in lines:
                if time.time() - start >= self.dur: break
                for ch in resolved:
                    try:
                        await ch.send(content=line)
                    except Exception as e:
                        log.error(f"Ошибка отправки в {ch.name}: {e}")
                await asyncio.sleep(3)


class ПодтверждениеРассылки(View):
    def __init__(self, uid: int, gid: int):
        super().__init__(timeout=60)
        self.uid = uid; self.gid = gid
        self.add_item(КнопкаЗакрыть(uid, gid, row=1))

    @discord.ui.button(label="START", style=discord.ButtonStyle.danger,
                       emoji="⚠️", row=0)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаРассылки(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary,
                       emoji="❌", row=0)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=tr(interaction.user.id, interaction.guild.id, "cancel_btn"),
            view=None)


class ПанельЗваний(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.sel_uid: int | None = None

        us = discord.ui.UserSelect(placeholder="Select member...",
                                   min_values=1, max_values=1, row=0)
        us.callback = self._on_user
        self.add_item(us)

        rs = Select(
            placeholder="Select rank...", min_values=1, max_values=1, row=1,
            options=[
                discord.SelectOption(label="1: Associato", value="1"),
                discord.SelectOption(label="2: Soldato", value="2"),
                discord.SelectOption(label="3: Capodecina", value="3"),
                discord.SelectOption(label="4: Sottocapo", value="4"),
                discord.SelectOption(label="5: Consigliere", value="5"),
                discord.SelectOption(label="👑 6: Capo di Tutti Capi", value="6"),
                discord.SelectOption(label="🔄 Reset", value="0"),
            ])
        rs.callback = self._on_rank
        self.add_item(rs)
        self.add_item(КнопкаЗакрыть(0, guild.id, row=2))

    async def _on_user(self, interaction: discord.Interaction):
        self.sel_uid = int(interaction.data["values"][0])
        await interaction.response.send_message(
            f"👤 <@{self.sel_uid}>. Now pick rank.", ephemeral=True)

    async def _on_rank(self, interaction: discord.Interaction):
        if not self.sel_uid:
            await interaction.response.send_message("❌ Select member first.",
                                                    ephemeral=True)
            return
        chosen = int(interaction.data["values"][0])
        st = получить_статы(interaction.guild.id, self.sel_uid)
        st["rank_override"] = chosen
        сохранить_данные()
        member = interaction.guild.get_member(self.sel_uid)
        if member:
            asyncio.create_task(проверить_роли(member, st["xp"], chosen))
        name = member.name if member else self.sel_uid
        label = ОТОБРАЖЕНИЕ_РАНГОВ.get(chosen, "Reset")
        await лог_админа(interaction.guild, interaction.user, "Rank change",
                         f"{name} → `{label}`")
        await interaction.response.send_message(
            f"✅ **{name}**: `{label}`", ephemeral=True)


class ПанельРолей(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.sel_uid: int | None = None
        self.sel_rid: int | None = None
        roles = [r for r in guild.roles
                 if not r.is_default() and not r.managed and r != guild.me.top_role]
        roles = sorted(roles, key=lambda r: r.position, reverse=True)

        us = discord.ui.UserSelect(placeholder="Member...", min_values=1,
                                   max_values=1, row=0)
        us.callback = self._on_user
        self.add_item(us)

        opts = [discord.SelectOption(label=r.name[:100], value=str(r.id))
                for r in roles[:25]]
        if not opts:
            opts.append(discord.SelectOption(label="No roles", value="0"))
        rs = Select(placeholder="Role...", min_values=1, max_values=1,
                    options=opts, row=1)
        rs.callback = self._on_role
        self.add_item(rs)
        self.add_item(КнопкаЗакрыть(0, guild.id, row=3))

    async def _on_user(self, interaction: discord.Interaction):
        self.sel_uid = int(interaction.data["values"][0])
        await interaction.response.send_message(
            f"👤 <@{self.sel_uid}>. Now role.", ephemeral=True)

    async def _on_role(self, interaction: discord.Interaction):
        self.sel_rid = int(interaction.data["values"][0])
        await interaction.response.send_message("🎭 Role selected.", ephemeral=True)

    @discord.ui.button(label="✅ Give", style=discord.ButtonStyle.success, row=2)
    async def give(self, button: Button, interaction: discord.Interaction):
        if not self.sel_uid or not self.sel_rid:
            await interaction.response.send_message("❌ Pick member and role.",
                                                    ephemeral=True)
            return
        m = interaction.guild.get_member(self.sel_uid)
        r = interaction.guild.get_role(self.sel_rid)
        if not m or not r:
            await interaction.response.send_message(tr(interaction.user.id,
                interaction.guild.id, "err_not_found"), ephemeral=True)
            return
        if r in m.roles:
            await interaction.response.send_message("❌ Already has it.",
                                                    ephemeral=True)
            return
        try:
            await m.add_roles(r, reason=f"DonCore: {interaction.user}")
            await лог_админа(interaction.guild, interaction.user, "Role given",
                             f"{m.mention} ← `{r.name}`")
            await interaction.response.send_message(f"✅ **{r.name}** → {m.mention}",
                                                    ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)

    @discord.ui.button(label="❌ Take", style=discord.ButtonStyle.danger, row=2)
    async def take(self, button: Button, interaction: discord.Interaction):
        if not self.sel_uid or not self.sel_rid:
            await interaction.response.send_message("❌ Pick member and role.",
                                                    ephemeral=True)
            return
        m = interaction.guild.get_member(self.sel_uid)
        r = interaction.guild.get_role(self.sel_rid)
        if not m or not r:
            await interaction.response.send_message("❌ Not found.", ephemeral=True)
            return
        if r not in m.roles:
            await interaction.response.send_message("❌ Doesn't have it.",
                                                    ephemeral=True)
            return
        try:
            await m.remove_roles(r, reason=f"DonCore: {interaction.user}")
            await лог_админа(interaction.guild, interaction.user, "Role removed",
                             f"{m.mention} ✖ `{r.name}`")
            await interaction.response.send_message(f"✅ Removed **{r.name}**",
                                                    ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)


class ПанельСимуляции(View):
    def __init__(self, gid: int):
        super().__init__(timeout=300)
        self.gid = gid
        self._собрать()

    def _собрать(self):
        self.clear_items()
        функции = [
            ("rank_roles", "🎖️ Ранги по XP"),
            ("verify", "🔗 Верификация"),
            ("shop", "🛒 Магазин"),
            ("automod", "🛡️ Авто-модерация"),
            ("mod_commands", "⚔️ Мод-команды"),
            ("all", "💥 ВСЕ СРАЗУ"),
        ]
        sim = _симуляция.get(self.gid, set())
        for i, (key, label) in enumerate(функции):
            вкл = key in sim
            icon = "🔴" if вкл else "🟢"
            btn = Button(
                label=f"{icon} {label}",
                style=discord.ButtonStyle.danger if вкл else discord.ButtonStyle.success,
                custom_id=f"sim_{key}_{i}",
                row=i // 2)
            btn.callback = self._make_cb(key)
            self.add_item(btn)
        close = Button(label="Chiudi", style=discord.ButtonStyle.secondary,
                       emoji="❌", row=3, custom_id="sim_close")
        close.callback = self._on_close
        self.add_item(close)

    def _make_cb(self, key: str):
        async def cb(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Don only.", ephemeral=True)
                return
            s = _симуляция.setdefault(self.gid, set())
            if key in s:
                s.discard(key)
            else:
                s.add(key)
            self._собрать()
            active = ", ".join(sorted(s)) if s else "—"
            await interaction.response.edit_message(
                content=f"🧪 **Симулятор ограничений**\n\n"
                        f"Изменено: `{key}`\n"
                        f"Активно выключено: `{active}`\n\n"
                        f"_Включи функции — бот начнёт отвечать ошибкой 403 "
                        f"при их использовании. Покажи овнеру._",
                view=self)
        return cb

    async def _on_close(self, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception:
            pass


class АдминПанель(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.add_item(КнопкаЗакрыть(0, guild.id, row=4))

    @discord.ui.button(label="Auto-reactions", style=discord.ButtonStyle.danger,
                       emoji="⚙️", row=0)
    async def reactions(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаРеакций(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="Ranks", style=discord.ButtonStyle.primary,
                       emoji="🎩", row=0)
    async def ranks(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("🎩 Ranks:",
                                                view=ПанельЗваний(interaction.guild),
                                                ephemeral=True)

    @discord.ui.button(label="Roles", style=discord.ButtonStyle.primary,
                       emoji="🎭", row=1)
    async def roles(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("🎭 Roles:",
                                                view=ПанельРолей(interaction.guild),
                                                ephemeral=True)

    @discord.ui.button(label="Money", style=discord.ButtonStyle.success,
                       emoji="💰", row=1)
    async def money(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаВыдатьДеньги(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="Broadcast", style=discord.ButtonStyle.danger,
                       emoji="🚨", row=2)
    async def abuse(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("⚠️ Broadcast:",
                                                view=ПодтверждениеРассылки(
                                                    interaction.user.id,
                                                    interaction.guild.id),
                                                ephemeral=True)

    @discord.ui.button(label="Give XP", style=discord.ButtonStyle.success,
                       emoji="⭐", row=2)
    async def xp(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаВыдатьXP(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="Don Core profile", style=discord.ButtonStyle.primary,
                       emoji="🎩", row=3)
    async def botprof(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаПрофильБота(bot, interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="🧪 Simulator", style=discord.ButtonStyle.secondary,
                       emoji="🧪", row=3)
    async def sim(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🧪 **Симулятор ограничений**\n\n"
            "Включай функции — когда выключена, бот отвечает **ошибкой 403**.\n"
            "Покажи овнеру: «вот так бот отвечает, когда роль низко».\n"
            "После выключения симуляции функции снова работают "
            "(но если роль бота реально низко — настоящий 403 всё равно вернётся).",
            view=ПанельСимуляции(interaction.guild.id),
            ephemeral=True)


class МодалкаВерификации(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "ver_title"))
        self.add_item(InputText(
            label=tr(uid, gid, "ver_label"),
            placeholder=tr(uid, gid, "ver_placeholder"),
            style=discord.InputTextStyle.short, required=True, max_length=20))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        username = self.children[0].value.strip()
        if not username:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        st = получить_статы(gid, uid)
        if st.get("verified"):
            await interaction.response.send_message(
                tr(uid, gid, "ver_already", nick=st.get("roblox_username")),
                ephemeral=True)
            return
        u = await roblox_по_нику(username)
        if not u:
            await interaction.response.send_message(tr(uid, gid, "ver_not_found"),
                                                    ephemeral=True)
            return
        code = сгенерировать_код()
        st["verify_code"] = code
        st["verify_code_expires"] = time.time() + ВРЕМЯ_КОДА
        сохранить_данные()
        embed = discord.Embed(
            title=tr(uid, gid, "ver_step2"),
            description=tr(uid, gid, "ver_step2_desc", rid=u["id"], code=code),
            color=discord.Color.dark_gold())
        await interaction.response.send_message(
            embed=embed,
            view=ПодтверждениеВерификации(u["id"], u["name"], uid, gid),
            ephemeral=True)


class ПодтверждениеВерификации(View):
    def __init__(self, rid: int, nick: str, uid: int, gid: int):
        super().__init__(timeout=ВРЕМЯ_КОДА)
        self.rid = rid; self.nick = nick
        self.uid = uid; self.gid = gid

    @discord.ui.button(label="Check", style=discord.ButtonStyle.success,
                       emoji="✅")
    async def check(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        st = получить_статы(gid, uid)
        if st.get("verified"):
            await interaction.response.send_message("✅ Already verified.",
                                                    ephemeral=True)
            return
        code = st.get("verify_code")
        exp = st.get("verify_code_expires", 0)
        if not code or time.time() > exp:
            await interaction.response.send_message(tr(uid, gid, "ver_expired"),
                                                    ephemeral=True)
            return
        desc = await roblox_описание(self.rid)
        if desc is None:
            await interaction.response.send_message(tr(uid, gid, "ver_no_profile"),
                                                    ephemeral=True)
            return
        if code not in desc:
            await interaction.response.send_message(
                tr(uid, gid, "ver_not_found_code", code=code), ephemeral=True)
            return

        if выключено(gid, "verify"):
            bot_top = interaction.guild.get_member(bot.user.id).top_role
            await interaction.response.send_message(
                f"❌ **Verification failed** for {interaction.user.mention}\n\n"
                f"Bot **cannot grant `{РОЛЬ_ВЕРИФИЦИРОВАН}` role**.\n\n"
                f"**Error:** `403 Forbidden` — Missing Permissions\n"
                f"**Error code:** `50013`\n"
                f"**Bot top role:** `{bot_top.name}` (`{bot_top.position}`)\n"
                f"**Fix:** raise bot role above `{РОЛЬ_ВЕРИФИЦИРОВАН}`.",
                ephemeral=True)
            return

        st["roblox_id"] = self.rid
        st["roblox_username"] = self.nick
        st["verified"] = True
        st["verify_code"] = None
        st["verify_code_expires"] = 0
        сохранить_данные()
        role = найти_роль(interaction.guild, РОЛЬ_ВЕРИФИЦИРОВАН)
        if role and role not in interaction.user.roles:
            try:
                await interaction.user.add_roles(role, reason="Roblox verifica")
            except Exception as e:
                log.warning(f"Не выдал Verified: {e}")
        try:
            await interaction.user.edit(nick=self.nick[:32])
        except Exception:
            pass
        await interaction.response.send_message(
            tr(uid, gid, "ver_success", nick=self.nick, rid=self.rid,
               role=РОЛЬ_ВЕРИФИЦИРОВАН), ephemeral=True)
        asyncio.create_task(выдать_достижение(interaction.guild, uid, "verified"))


class ПанельКазино(View):
    def __init__(self, uid: int):
        super().__init__(timeout=60)
        self.uid = uid
        self.add_item(КнопкаЗакрыть(uid, 0, row=1))

    @discord.ui.button(label="🎲 100", style=discord.ButtonStyle.primary, row=0)
    async def b100(self, button: Button, interaction: discord.Interaction):
        await self._run(interaction, 100)

    @discord.ui.button(label="🔥 500", style=discord.ButtonStyle.success, row=0)
    async def b500(self, button: Button, interaction: discord.Interaction):
        await self._run(interaction, 500)

    @discord.ui.button(label="💀 ALL-IN", style=discord.ButtonStyle.danger, row=0)
    async def ball(self, button: Button, interaction: discord.Interaction):
        st = получить_статы(interaction.guild.id, interaction.user.id)
        await self._run(interaction, st["coins"], all_in=True)

    async def _run(self, interaction: discord.Interaction, amount: int,
                   all_in: bool = False):
        uid = interaction.user.id; gid = interaction.guild.id
        if uid != self.uid:
            await interaction.response.send_message(tr(uid, gid, "casino_not_yours"),
                                                    ephemeral=True)
            return
        st = получить_статы(gid, uid)
        if amount <= 0:
            await interaction.response.send_message(tr(uid, gid, "casino_no_money"),
                                                    ephemeral=True)
            return
        if st["coins"] < amount:
            await interaction.response.send_message(
                tr(uid, gid, "casino_not_en", balance=st["coins"]), ephemeral=True)
            return
        rem = кд_казино_ок(gid, uid)
        if rem > 0:
            await interaction.response.send_message(
                tr(uid, gid, "casino_cd", sec=rem), ephemeral=True)
            return

        сбросить_миссии(st)
        st["missions"]["casino_played"] += 1

        await interaction.response.send_message(
            tr(uid, gid, "casino_spin", user=interaction.user.mention, amount=amount))
        msg = await interaction.original_response()
        await asyncio.sleep(1.2)
        await msg.edit(content=tr(uid, gid, "casino_stop",
                                  user=interaction.user.mention, amount=amount))
        await asyncio.sleep(1.2)

        won = random.random() < 0.30
        secret = False
        if all_in and st["coins"] >= 10000 and random.random() < 0.001:
            secret = True; won = True

        if won:
            r = random.random()
            if r < 0.01:
                mult, tier = 10, tr(uid, gid, "casino_jackpot")
            elif r < 0.30:
                mult, tier = 5, tr(uid, gid, "casino_bigwin")
            else:
                mult, tier = 2, tr(uid, gid, "casino_win")
            profit = amount * mult
            st["coins"] += profit
            st["missions"]["casino_wins"] = st["missions"].get("casino_wins", 0) + 1
            if mult == 10:
                st["total_casino_jackpots"] = st.get("total_casino_jackpots", 0) + 1
                asyncio.create_task(выдать_достижение(interaction.guild, uid, "jackpot"))
            role_msg = ""
            if secret:
                role = найти_роль(interaction.guild, РОЛЬ_СЕКРЕТНАЯ)
                if role:
                    try:
                        await interaction.user.add_roles(role)
                        role_msg = f"\n👑 **{role.name}**!"
                    except Exception:
                        role_msg = ""
            result = tr(uid, gid, "casino_res_win", tier=tier, mult=mult,
                        user=interaction.user.mention, profit=profit,
                        balance=st["coins"], role_msg=role_msg)
        else:
            st["coins"] -= amount
            result = tr(uid, gid, "casino_res_lose",
                        title=tr(uid, gid, "casino_lose"),
                        user=interaction.user.mention, amount=amount,
                        balance=st["coins"])
        сохранить_данные()
        await msg.edit(content=result, view=None)


class ПанельМиссий(View):
    def __init__(self, uid: int, gid: int):
        super().__init__(timeout=60)
        self.uid = uid; self.gid = gid

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success,
                       emoji="🎁", row=0)
    async def claim(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        if uid != self.uid:
            await interaction.response.send_message(tr(uid, gid, "m_not_yours"),
                                                    ephemeral=True)
            return
        st = получить_статы(gid, uid)
        сбросить_миссии(st)
        m = st["missions"]
        claimed = m["claimed"]
        coins = 0; xp = 0
        rewards = [
            ("msg", 5, m.get("msg_count", 0), 500, 200),
            ("media", 3, m.get("media_count", 0), 1500, 500),
            ("casino", 3, m.get("casino_played", 0), 2000, 500),
            ("casino_win", 3, m.get("casino_wins", 0), 3000, 240),
            ("duel_win", 1, m.get("duel_wins", 0), 1500, 100),
            ("transfer", 1, m.get("transfer_sent", 0), 500, 50),
            ("shop", 1, m.get("shop_bought", 0), 2000, 100),
            ("poll", 1, m.get("poll_voted", 0), 800, 400),
            ("roll", 1, m.get("roll_high", 0), 500, 80),
            ("furry", 1, m.get("furry_triggered", 0), 1000, 400),
        ]
        for k, tgt, cur, c_r, x_r in rewards:
            if k not in claimed and cur >= tgt:
                coins += c_r; xp += x_r; claimed.append(k)
        if "daily" not in claimed and m.get("daily_claimed", 0) >= 1:
            s = st.get("streak_days", 1)
            dxp = min(10 + (s - 1) * 20, 200)
            coins += 700; xp += dxp; claimed.append("daily")
        if st["xp"] >= 10000 and "hardcore" not in claimed:
            coins += 10000; claimed.append("hardcore")

        if coins > 0 or xp > 0:
            st["coins"] += coins
            st["xp"] += xp
            сохранить_данные()
            if st.get("rank_override", 0) == 0 and isinstance(interaction.user, discord.Member):
                asyncio.create_task(проверить_роли(interaction.user, st["xp"],
                                                   st["rank_override"]))
            await interaction.response.send_message(
                tr(uid, gid, "m_claimed_ok", coins=coins, xp=xp), ephemeral=True)
        else:
            await interaction.response.send_message(tr(uid, gid, "m_no_rewards"),
                                                    ephemeral=True)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.secondary,
                       emoji="❌", row=1)
    async def close(self, button: Button, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception:
            pass


class ПанельМагазина(View):
    def __init__(self, uid: int, gid: int):
        super().__init__(timeout=180)
        self.uid = uid; self.gid = gid
        opts = []
        for key, item in ТОВАРЫ.items():
            desc = tr(uid, gid, item["desc_key"])[:100]
            opts.append(discord.SelectOption(
                label=f"{item['emoji']} {item['label']} — {item['price']} 💰",
                value=key, description=desc))
        sel = Select(placeholder=tr(uid, gid, "shop_placeholder"),
                     options=opts, row=0)
        sel.callback = self._on_buy
        self.add_item(sel)
        self.add_item(КнопкаЗакрыть(uid, gid, row=1))

    async def _on_buy(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        if uid != self.uid:
            await interaction.response.send_message(tr(uid, gid, "shop_not_yours"),
                                                    ephemeral=True)
            return
        key = interaction.data["values"][0]
        item = ТОВАРЫ.get(key)
        if not item:
            await interaction.response.send_message("❌", ephemeral=True)
            return
        st = получить_статы(gid, uid)
        if item["price"] > st["coins"]:
            await interaction.response.send_message(
                tr(uid, gid, "shop_no_money", price=item["price"], have=st["coins"]),
                ephemeral=True)
            return

        if item["role_name"] is None:
            if key == "profile_bg":
                if "profile_bg" in st.get("inventory", []):
                    await interaction.response.send_message(
                        tr(uid, gid, "shop_owned"), ephemeral=True)
                    return
                st["coins"] -= item["price"]
                st.setdefault("inventory", []).append("profile_bg")
                st["missions"]["shop_bought"] = st["missions"].get("shop_bought", 0) + 1
                сохранить_данные()
                await interaction.response.send_message(
                    tr(uid, gid, "shop_bg_ok"), ephemeral=True)
                return
            if item["label"] in st.get("titles", []):
                await interaction.response.send_message(tr(uid, gid, "shop_owned"),
                                                        ephemeral=True)
                return
            st["coins"] -= item["price"]
            st.setdefault("titles", []).append(item["label"])
            st["missions"]["shop_bought"] = st["missions"].get("shop_bought", 0) + 1
            сохранить_данные()
            await interaction.response.send_message(
                tr(uid, gid, "shop_bought", item=f"{item['emoji']} {item['label']}",
                   price=item["price"]), ephemeral=True)
            return

        if выключено(gid, "shop"):
            await interaction.response.send_message(
                f"❌ **Purchase failed** for {interaction.user.mention}\n\n"
                f"Bot **cannot grant role** `{item['role_name']}`.\n\n"
                f"**Error:** `403 Forbidden` — Missing Permissions\n"
                f"**Error code:** `50013`\n"
                f"**Fix:** raise bot role above `{item['role_name']}`.",
                ephemeral=True)
            return

        role = найти_роль(interaction.guild, item["role_name"])
        if role is None:
            await interaction.response.send_message(
                tr(uid, gid, "shop_role_missing", role=item["role_name"]),
                ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message(tr(uid, gid, "shop_owned"),
                                                    ephemeral=True)
            return
        st["coins"] -= item["price"]
        st.setdefault("inventory", []).append(key)
        st["missions"]["shop_bought"] = st["missions"].get("shop_bought", 0) + 1
        сохранить_данные()
        try:
            await interaction.user.add_roles(role, reason=f"DonCore shop: {key}")
        except Exception as e:
            log.warning(f"Не выдал роль {role.name}: {e}")
        await interaction.response.send_message(
            tr(uid, gid, "shop_role_given", role=role.name), ephemeral=True)


class ПодтверждениеДуэли(View):
    def __init__(self, ch_id: int, tg_id: int, amount: int, gid: int):
        super().__init__(timeout=ТАЙМАУТ_ДУЭЛИ)
        self.ch_id = ch_id; self.tg_id = tg_id
        self.amount = amount; self.gid = gid
        self.done = False

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        if uid != self.tg_id:
            await interaction.response.send_message(tr(uid, gid, "duel_not_yours"),
                                                    ephemeral=True)
            return
        if self.done:
            await interaction.response.send_message(tr(uid, gid, "duel_ended"),
                                                    ephemeral=True)
            return
        self.done = True
        ch_st = получить_статы(gid, self.ch_id)
        tg_st = получить_статы(gid, self.tg_id)
        if ch_st["coins"] < self.amount:
            await interaction.response.edit_message(
                content=tr(uid, gid, "duel_ch_no_money", ch=self.ch_id, amount=self.amount),
                view=None)
            return
        if tg_st["coins"] < self.amount:
            await interaction.response.send_message(
                tr(uid, gid, "duel_tg_no_money", amount=self.amount), ephemeral=True)
            return
        winner = random.choice([self.ch_id, self.tg_id])
        loser = self.tg_id if winner == self.ch_id else self.ch_id
        получить_статы(gid, winner)["coins"] += self.amount
        получить_статы(gid, loser)["coins"] -= self.amount
        получить_статы(gid, winner)["missions"]["duel_wins"] = \
            получить_статы(gid, winner)["missions"].get("duel_wins", 0) + 1
        сохранить_данные()
        await interaction.response.edit_message(
            content=tr(uid, gid, "duel_result", ch=f"<@{self.ch_id}>",
                       tg=f"<@{self.tg_id}>", amount=self.amount, win=winner),
            view=None)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        if uid != self.tg_id:
            await interaction.response.send_message(tr(uid, gid, "duel_not_yours"),
                                                    ephemeral=True)
            return
        if self.done: return
        self.done = True
        await interaction.response.edit_message(
            content=tr(uid, gid, "duel_declined", tg=self.tg_id), view=None)


class МодалкаБага(Modal):
    def __init__(self, cat: str, uid: int, gid: int):
        title_key = "bug_title_g" if cat == "game" else "bug_title_s"
        super().__init__(title=tr(uid, gid, title_key))
        self.cat = cat
        self.add_item(InputText(label=tr(uid, gid, "bug_name"),
                                placeholder=tr(uid, gid, "bug_name_ph"),
                                style=discord.InputTextStyle.short,
                                required=True, max_length=100))
        self.add_item(InputText(label=tr(uid, gid, "bug_desc"),
                                placeholder=tr(uid, gid, "bug_desc_ph"),
                                style=discord.InputTextStyle.paragraph,
                                required=True, max_length=500))
        self.add_item(InputText(label=tr(uid, gid, "bug_steps"),
                                placeholder=tr(uid, gid, "bug_steps_ph"),
                                style=discord.InputTextStyle.paragraph,
                                required=True, max_length=500))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        title = self.children[0].value.strip()
        desc = self.children[1].value.strip()
        steps = self.children[2].value.strip()

        if self.cat == "game":
            ch_name = КАНАЛ_БАГОВ_ИГРЫ; emoji = "🎮"
            tl = tr(uid, gid, "bug_type_g")
        else:
            ch_name = КАНАЛ_БАГОВ_СЕРВЕРА; emoji = "🖥️"
            tl = tr(uid, gid, "bug_type_s")

        ch = найти_канал(interaction.guild, ch_name)
        if not ch:
            await interaction.response.send_message(
                tr(uid, gid, "bug_channel_no", ch=ch_name), ephemeral=True)
            return

        bug_id = f"B{int(time.time())}"
        s = получить_настройки(gid)
        s["bugs"][bug_id] = {"author_id": uid, "title": title,
                             "category": self.cat, "status": "open"}
        сохранить_настройки()

        embed = discord.Embed(
            title=f"{emoji} {title}",
            description=(f"**{tr(uid, gid, 'bug_reporter')}:** {interaction.user.mention}\n"
                         f"**ID:** `{bug_id}`\n**{tr(uid, gid, 'bug_type')}:** {tl}"),
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc))
        embed.add_field(name=f"📝 {tr(uid, gid, 'bug_desc')}", value=desc[:1024],
                        inline=False)
        embed.add_field(name=f"🔁 {tr(uid, gid, 'bug_steps')}", value=steps[:1024],
                        inline=False)
        embed.add_field(name=f"📊 {tr(uid, gid, 'bug_status')}",
                        value=tr(uid, gid, "bug_open"), inline=False)

        msg = await ch.send(embed=embed, view=СтатусыБагов(bug_id, uid, gid))
        s["bugs"][bug_id]["message_id"] = msg.id
        сохранить_настройки()
        await interaction.response.send_message(
            tr(uid, gid, "bug_created", url=msg.jump_url), ephemeral=True)


class СтатусыБагов(View):
    def __init__(self, bug_id: str, uid: int, gid: int):
        super().__init__(timeout=None)
        self.bug_id = bug_id

    @discord.ui.button(label="WIP", style=discord.ButtonStyle.primary,
                       custom_id="bug_wip", emoji="🔧")
    async def wip(self, button: Button, interaction: discord.Interaction):
        await self._set(interaction, "wip", "bug_wip")

    @discord.ui.button(label="Fixed", style=discord.ButtonStyle.success,
                       custom_id="bug_fixed", emoji="✅")
    async def fixed(self, button: Button, interaction: discord.Interaction):
        await self._set(interaction, "fixed", "bug_fixed")

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger,
                       custom_id="bug_rejected", emoji="❌")
    async def rejected(self, button: Button, interaction: discord.Interaction):
        await self._set(interaction, "rejected", "bug_rejected")

    async def _set(self, interaction: discord.Interaction, status: str, label_key: str):
        uid = interaction.user.id; gid = interaction.guild.id
        s = получить_настройки(gid)
        bug = s["bugs"].get(self.bug_id)
        if not bug:
            await interaction.response.send_message(tr(uid, gid, "err_not_found"),
                                                    ephemeral=True)
            return
        is_admin = (interaction.user.guild_permissions.administrator or
                    interaction.user.guild_permissions.manage_messages)
        is_author = uid == bug["author_id"]
        if not (is_admin or is_author):
            await interaction.response.send_message(tr(uid, gid, "bug_no_access"),
                                                    ephemeral=True)
            return
        bug["status"] = status
        сохранить_настройки()
        embed = interaction.message.embeds[0]
        for i, f in enumerate(embed.fields):
            if f.name.startswith("📊"):
                embed.set_field_at(i, name=f"📊 {tr(uid, gid, 'bug_status')}",
                                   value=tr(uid, gid, label_key), inline=False)
                break
        await interaction.response.edit_message(embed=embed)


class МодалкаПредложения(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "sug_title"))
        self.add_item(InputText(label=tr(uid, gid, "sug_label"),
                                placeholder=tr(uid, gid, "sug_ph"),
                                style=discord.InputTextStyle.paragraph,
                                required=True, max_length=1000))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        text = self.children[0].value.strip()
        log_ch = найти_канал(interaction.guild, КАНАЛ_ЛОГОВ)
        if not log_ch:
            await interaction.response.send_message(tr(uid, gid, "sug_no_log"),
                                                    ephemeral=True)
            return
        sid = f"S{int(time.time())}"
        s = получить_настройки(gid)
        s["suggestions"][sid] = {"author_id": uid, "text": text, "status": "pending"}
        сохранить_настройки()

        embed = discord.Embed(
            title=tr(uid, gid, "sug_pending"),
            description=text[:4000],
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc))
        embed.set_author(name=interaction.user.display_name,
                         icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"ID: {sid}")
        msg = await log_ch.send(embed=embed, view=МодерацияПредложения(sid, uid, gid))
        s["suggestions"][sid]["mod_message_id"] = msg.id
        сохранить_настройки()
        await interaction.response.send_message(tr(uid, gid, "sug_sent"),
                                                ephemeral=True)


class МодерацияПредложения(View):
    def __init__(self, sid: str, uid: int, gid: int):
        super().__init__(timeout=None)
        self.sid = sid

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success,
                       custom_id="sug_ok", emoji="✅")
    async def approve(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        if not (interaction.user.guild_permissions.administrator or
                interaction.user.guild_permissions.manage_messages):
            await interaction.response.send_message(tr(uid, gid, "sug_don_only"),
                                                    ephemeral=True)
            return
        s = получить_настройки(gid)
        sug = s["suggestions"].get(self.sid)
        if not sug or sug["status"] != "pending":
            await interaction.response.send_message(tr(uid, gid, "sug_processed"),
                                                    ephemeral=True)
            return
        sug["status"] = "approved"
        сохранить_настройки()

        ch = найти_канал(interaction.guild, КАНАЛ_ПРЕДЛОЖЕНИЙ)
        if not ch:
            await interaction.response.send_message(
                tr(uid, gid, "sug_channel_no", ch=КАНАЛ_ПРЕДЛОЖЕНИЙ), ephemeral=True)
            return
        author = interaction.guild.get_member(sug["author_id"])
        embed = discord.Embed(
            title=tr(uid, gid, "sug_pub_title"),
            description=sug["text"][:4000],
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc))
        if author:
            embed.set_author(name=author.display_name,
                             icon_url=author.display_avatar.url)
        embed.set_footer(text=f"ID: {self.sid}")
        msg = await ch.send(embed=embed)
        for e in ["👍", "👎", "🤔", "🔥"]:
            try:
                await msg.add_reaction(e)
            except Exception:
                pass
        sug["public_message_id"] = msg.id
        сохранить_настройки()
        await interaction.response.send_message(
            tr(uid, gid, "sug_published", url=msg.jump_url), ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger,
                       custom_id="sug_no", emoji="❌")
    async def reject(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        if not (interaction.user.guild_permissions.administrator or
                interaction.user.guild_permissions.manage_messages):
            await interaction.response.send_message(tr(uid, gid, "sug_don_only"),
                                                    ephemeral=True)
            return
        s = получить_настройки(gid)
        sug = s["suggestions"].get(self.sid)
        if not sug or sug["status"] != "pending":
            await interaction.response.send_message(tr(uid, gid, "sug_processed"),
                                                    ephemeral=True)
            return
        sug["status"] = "rejected"
        сохранить_настройки()
        try:
            await interaction.message.delete()
        except Exception:
            pass
        await interaction.response.send_message(tr(uid, gid, "sug_rejected"),
                                                ephemeral=True)


class ПрофильКнопки(View):
    def __init__(self, uid: int | None = None):
        super().__init__(timeout=180)
        self.uid = uid

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary,
                       emoji="🔄", row=0)
    async def refresh(self, button: Button, interaction: discord.Interaction):
        tid = self.uid or interaction.user.id
        st = получить_статы(interaction.guild.id, tid)
        m = interaction.guild.get_member(tid) or interaction.user
        await interaction.response.edit_message(embed=эмбед_профиля(st, m), view=self)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.secondary,
                       emoji="❌", row=0)
    async def close(self, button: Button, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception:
            pass


class ГлавнаяПанель(View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Profile", style=discord.ButtonStyle.primary,
                       emoji="🎩", row=0)
    async def profile(self, button: Button, interaction: discord.Interaction):
        st = получить_статы(interaction.guild.id, interaction.user.id)
        await interaction.response.send_message(
            embed=эмбед_профиля(st, interaction.user),
            view=ПрофильКнопки(), ephemeral=True)

    @discord.ui.button(label="Don's office", style=discord.ButtonStyle.success,
                       emoji="🔐", row=0)
    async def admin(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаПароль(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="Close", style=discord.ButtonStyle.secondary,
                       emoji="❌", row=1)
    async def close(self, button: Button, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception:
            pass


class КнопкаЗакрытияОпроса(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close poll", style=discord.ButtonStyle.danger,
                       emoji="🔒")
    async def close_poll(self, button: Button, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        is_author = (interaction.message.interaction and
                     interaction.message.interaction.user.id == uid)
        if not (is_author or interaction.user.guild_permissions.manage_messages):
            await interaction.response.send_message(tr(uid, gid, "poll_no_rights"),
                                                    ephemeral=True)
            return
        msg = interaction.message
        results = [(str(r.emoji), r.count - 1) for r in msg.reactions]
        results.sort(key=lambda x: x[1], reverse=True)
        lines = "\n".join(f"{e} — **{c}**" for e, c in results)
        winner = results[0] if results and results[0][1] > 0 else None
        embed = msg.embeds[0] if msg.embeds else discord.Embed()
        embed.add_field(name=tr(uid, gid, "poll_results"),
                        value=lines or tr(uid, gid, "poll_none"), inline=False)
        if winner:
            embed.add_field(name=tr(uid, gid, "poll_winner"),
                            value=winner[0], inline=False)
        embed.color = discord.Color.dark_grey()
        await msg.edit(embed=embed, view=None)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == (bot.user.id if bot.user else 0): return
    if not payload.guild_id: return
    guild = bot.get_guild(payload.guild_id)
    if not guild: return
    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.TextChannel): return
    try:
        msg = await channel.fetch_message(payload.message_id)
    except Exception:
        return
    if not msg.embeds or not msg.author.bot: return
    title = msg.embeds[0].title or ""
    if not title.startswith("📊"): return
    st = получить_статы(guild.id, payload.user_id)
    if not st["missions"].get("poll_voted"):
        st["missions"]["poll_voted"] = 1
        сохранить_данные()


# ============================================================
# ПОКЕР — ЛОГИКА
# ============================================================
def _пк_колода():
    d = [(r, s) for s in _ПК_МАСТИ for r in range(2, 15)]
    random.shuffle(d); return d


def _пк_карта(c): return f"`{_ПК_СИМВ[c[0]]}{c[1]}`"


def _пк_карты(cards, hidden=False):
    if not cards: return "—"
    if hidden: return "🎴  🎴"
    return "  ".join(_пк_карта(c) for c in cards)


def _пк_оценить(cards):
    from collections import Counter
    ranks = [c[0] for c in cards]; suits = [c[1] for c in cards]
    cnt = Counter(ranks); srt = sorted(cnt.items(), key=lambda x: (-x[1], -x[0]))

    fm = None
    for s in set(suits):
        if suits.count(s) >= 5: fm = s; break

    uniq = sorted(set(ranks), reverse=True); st = None
    for i in range(len(uniq)-4):
        if uniq[i] - uniq[i+4] == 4: st = uniq[i]; break
    if 14 in uniq and all(x in uniq for x in [2,3,4,5]):
        if not st or st < 5: st = 5

    if fm:
        fr = sorted([c[0] for c in cards if c[1] == fm], reverse=True)
        for i in range(len(fr)-4):
            if fr[i] - fr[i+4] == 4:
                return (8, (14,), "Royal Flush 🌟") if fr[i] == 14 else (8, (fr[i],), "Straight Flush")
        if 14 in fr and all(x in fr for x in [2,3,4,5]):
            return (8, (5,), "Straight Flush")

    if srt[0][1] == 4:
        q = srt[0][0]; k = max(r for r in ranks if r != q)
        return (7, (q, k), "Four of a Kind")

    trips = [x for x in srt if x[1] == 3]; pairs = [x for x in srt if x[1] == 2]
    if trips and len(trips) >= 2:
        return (6, (trips[0][0], trips[1][0]), "Full House")
    if trips and pairs:
        return (6, (trips[0][0], pairs[0][0]), "Full House")

    if fm:
        fr = sorted([c[0] for c in cards if c[1] == fm], reverse=True)[:5]
        return (5, tuple(fr), "Flush")
    if st: return (4, (st,), "Straight")
    if srt[0][1] == 3:
        t = srt[0][0]; k = tuple(x[0] for x in srt[1:3])
        return (3, (t,)+k, "Three of a Kind")
    if len(pairs) >= 2:
        top = (pairs[0][0], pairs[1][0])
        k = max(r for r in ranks if r not in top)
        return (2, top+(k,), "Two Pair")
    if srt[0][1] == 2:
        p = srt[0][0]; k = tuple(x[0] for x in srt[1:4])
        return (1, (p,)+k, "Pair")
    return (0, tuple(sorted(ranks, reverse=True)[:5]), "High Card")


def _пк_рендер(s, reveal=False):
    uid_tr = s["players"][0] if s["players"] else 0
    e = discord.Embed(title=tr(uid_tr, s.get("gid", 0), "pk_table_title"),
                      color=discord.Color.dark_green())
    stage = {"preflop":"Pre-flop","flop":"Flop","turn":"Turn",
             "river":"River","showdown":"Showdown"}.get(s["stage"], s["stage"])
    line = f"💰 **Банк:** `{s['pot']}`"
    if s["current_bet"] > 0:
        line += f"  •  Ставка раунда: `{s['current_bet']}`"
    if s.get("sb") and s.get("bb"):
        line += f"  •  Блайнды: `{s['sb']}/{s['bb']}`"
    e.description = line

    n = len(s["players"]); dealer_uid = s["players"][s["dealer_idx"]]
    if n == 2:
        sb_uid = dealer_uid; bb_uid = s["players"][(s["dealer_idx"]+1)%n]
    else:
        sb_uid = s["players"][(s["dealer_idx"]+1)%n]
        bb_uid = s["players"][(s["dealer_idx"]+2)%n]

    lines = []
    for uid in s["players"]:
        stack = s["stacks"][uid]; bet = s["bets"][uid]; tags = []
        if uid == sb_uid: tags.append("🔵 SB")
        if uid == bb_uid: tags.append("🔴 BB")
        if uid in s["folded"]: tags.append("❌ fold")
        elif uid in s["all_in"]: tags.append("🔥 ALL-IN")
        elif uid == s["players"][s["current_idx"]] and not s["finished"]:
            tags.append("🎯 **ход**")
        tag_str = " • ".join(tags)
        
        # ФИКС: скрываем карты фолдеров даже на шоудауне
        hand_str = "🎴  🎴"
        if (reveal or s["stage"] == "showdown") and uid not in s["folded"]:
            hand_str = _пк_карты(s["hole"][uid])
            
        l = f"<@{uid}> — стек `{stack}` • ставка `{bet}`"
        if tag_str: l += f"\n  {tag_str}"
        l += f"\n  {hand_str}"
        lines.append(l)

    e.add_field(name=f"👥 {tr(uid_tr, s['gid'], 'pk_players')} ({n})", value="\n".join(lines), inline=False)
    e.add_field(name=f"📋 {stage}",
                value=_пк_карты(s["community"]) if s["community"] else "—",
                inline=False)
    e.add_field(name=tr(uid_tr, s['gid'], "pk_dealer"),
                value=f"\n\n**<@{dealer_uid}>**\n\n",
                inline=False)
    return e


def _пк_разбить_банк(state):
    contrib = state["contributed"]
    active_uids = [u for u in state["players"] if u not in state["folded"]]
    уровни = sorted(set(contrib[u] for u in contrib if contrib[u] > 0))
    банки = []
    предыдущий = 0
    for уровень in уровни:
        вкладчики = [u for u in contrib if contrib[u] >= уровень]
        сумма = (уровень - предыдущий) * len(вкладчики)
        претенденты = [u for u in вкладчики if u in active_uids]
        if претенденты:
            банки.append((сумма, претенденты))
        предыдущий = уровень
    return банки


class ПКЛобби(View):
    def __init__(self, host_id, gid, buyin, min_p, max_p, turn_time):
        super().__init__(timeout=600)
        self.host_id = host_id; self.gid = gid; self.buyin = buyin
        self.min_p = min_p; self.max_p = max_p; self.turn_time = turn_time
        self.players = [host_id]; self.started = False; self.thread_id = None
        self._rebuild()

    def _эмбед(self):
        bb = max(20, self.buyin // 50)
        sb = bb // 2
        lines = "\n".join(f"• <@{p}>" for p in self.players)
        e = discord.Embed(title=tr(self.host_id, self.gid, "pk_lobby_title"),
                          description=(f"{tr(self.host_id, self.gid, 'pk_buyin')}: `{self.buyin}` 💰\n"
                                       f"{tr(self.host_id, self.gid, 'pk_blinds')}: `{sb}/{bb}`\n"
                                       f"{tr(self.host_id, self.gid, 'pk_turn_time')}: `{self.turn_time} сек`\n"
                                       f"{tr(self.host_id, self.gid, 'pk_players')}: `{len(self.players)}/{self.max_p}` "
                                       f"(мин `{self.min_p}`)\n\n**{tr(self.host_id, self.gid, 'pk_at_table')}**\n{lines}"),
                          color=discord.Color.dark_gold())
        if len(self.players) < self.min_p:
            e.set_footer(text=tr(self.host_id, self.gid, "pk_need_more").format(self.min_p - len(self.players)))
        else:
            e.set_footer(text=tr(self.host_id, self.gid, "pk_host_start"))
        return e

    def _rebuild(self):
        self.clear_items()
        j = Button(label=tr(self.host_id, self.gid, "pk_join_btn"), style=discord.ButtonStyle.success,
                   emoji="🎯", custom_id="pkl_join")
        j.callback = self._join; self.add_item(j)
        s = Button(label=tr(self.host_id, self.gid, "pk_start_btn"), style=discord.ButtonStyle.danger,
                   emoji="▶️", custom_id="pkl_start")
        s.callback = self._start; self.add_item(s)
        l = Button(label=tr(self.host_id, self.gid, "pk_leave_btn"), style=discord.ButtonStyle.secondary,
                   emoji="🚪", custom_id="pkl_leave")
        l.callback = self._leave; self.add_item(l)

    async def _join(self, interaction):
        if self.started:
            await interaction.response.send_message("❌ Игра идёт.", ephemeral=True); return
        uid = interaction.user.id
        if uid in self.players:
            await interaction.response.send_message("❌ Вы уже в столе.", ephemeral=True); return
        if len(self.players) >= self.max_p:
            await interaction.response.send_message("❌ Стол полон.", ephemeral=True); return
        st = получить_статы(self.gid, uid)
        if st["coins"] < self.buyin:
            await interaction.response.send_message(f"❌ Нужно **{self.buyin}** 💰.",
                                                    ephemeral=True); return
        self.players.append(uid); self._rebuild()
        await interaction.response.edit_message(embed=self._эмбед(), view=self)

    async def _leave(self, interaction):
        uid = interaction.user.id
        if self.started:
            await interaction.response.send_message("❌ Поздно.", ephemeral=True); return
        if uid not in self.players:
            await interaction.response.send_message("❌ Вас нет в столе.", ephemeral=True); return
        self.players.remove(uid)
        if not self.players:
            await interaction.response.edit_message(content="❌ Стол закрыт.",
                                                    embed=None, view=None); return
        if uid == self.host_id: self.host_id = self.players[0]
        self._rebuild()
        await interaction.response.edit_message(embed=self._эмбед(), view=self)

    async def _start(self, interaction):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("❌ Только хост.", ephemeral=True); return
        if len(self.players) < self.min_p:
            await interaction.response.send_message(
                f"❌ Нужно минимум **{self.min_p}**. Сейчас `{len(self.players)}`.",
                ephemeral=True); return
        self.started = True
        for uid in self.players:
            st = получить_статы(self.gid, uid); st["coins"] -= self.buyin
            st["missions"]["casino_played"] = st["missions"].get("casino_played", 0) + 1
        сохранить_данные()
        await _пк_старт(interaction, self)


async def _пк_старт(interaction, lobby):
    gid = lobby.gid; players = lobby.players; deck = _пк_колода()
    thread_id = lobby.thread_id
    thread = bot.get_channel(thread_id) if thread_id else interaction.channel

    bb = max(20, lobby.buyin // 50)
    sb = bb // 2

    state = {
        "players": players,
        "stacks": {uid: lobby.buyin for uid in players},
        "bets": {uid: 0 for uid in players},
        "contributed": {uid: 0 for uid in players},
        "acted": set(),
        "folded": set(), "all_in": set(),
        "hole": {uid: [deck.pop(), deck.pop()] for uid in players},
        "community": [], "deck": deck, "pot": 0, "stage": "preflop",
        "dealer_idx": random.randint(0, len(players)-1),
        "current_idx": 0, "current_bet": 0, "min_raise": bb,
        "sb": sb, "bb": bb,
        "last_raiser_idx": None, "bet": lobby.buyin, "gid": gid,
        "thread_id": thread_id, "public_msg_id": None,
        "finished": False, "turn_time": lobby.turn_time,
        "started_at": time.time(),
    }

    n = len(players)
    if n == 2: sb_idx, bb_idx = state["dealer_idx"], (state["dealer_idx"]+1)%n
    else: sb_idx, bb_idx = (state["dealer_idx"]+1)%n, (state["dealer_idx"]+2)%n

    sb_uid, bb_uid = players[sb_idx], players[bb_idx]
    sb_a = min(sb, state["stacks"][sb_uid])
    bb_a = min(bb, state["stacks"][bb_uid])
    state["stacks"][sb_uid] -= sb_a; state["stacks"][bb_uid] -= bb_a
    state["bets"][sb_uid] = sb_a; state["bets"][bb_uid] = bb_a
    state["contributed"][sb_uid] += sb_a; state["contributed"][bb_uid] += bb_a
    state["pot"] = sb_a + bb_a; state["current_bet"] = bb_a
    state["current_idx"] = sb_idx if n == 2 else (bb_idx+1)%n

    # ФИКС: сохраняем ID лобби-сообщения, чтобы удалить его в конце
    try:
        await interaction.response.edit_message(embed=_пк_рендер(state), view=None)
        lobby_msg = await interaction.original_response()
        state["parent_msg_id"] = lobby_msg.id
        state["parent_channel_id"] = lobby_msg.channel.id
    except Exception as e: 
        log.warning(f"Не удалось запомнить лобби-сообщение: {e}")

    try:
        m = await thread.send(embed=_пк_рендер(state))
        state["public_msg_id"] = m.id
    except Exception as e:
        log.error(f"Не отправил старт в ветку: {e}"); return

    _покер_толы[state["public_msg_id"]] = state
    _покер_сохранить()
    for uid in players:
        await _пк_эфе_ход(state, uid)


async def _пк_эфе_ход(state, uid):
    if uid in state["folded"]: return
    if uid in state["all_in"]: return
    if state.get("finished"): return
    hand = state["hole"][uid]; stack = state["stacks"][uid]
    my_bet = state["bets"][uid]; to_call = max(0, state["current_bet"] - my_bet)
    is_current = state["players"][state["current_idx"]] == uid
    gid = state.get("gid", 0)

    e = discord.Embed(title=tr(uid, gid, "pk_your_hand"), color=discord.Color.dark_green())
    e.add_field(name=tr(uid, gid, "pk_cards"), value=_пк_карты(hand), inline=False)

    stage_ru = {"preflop":"Pre-flop","flop":"Flop","turn":"Тёрн",
                "river":"Ривер","showdown":"Showdown"}.get(state["stage"], state["stage"])
    board = _пк_карты(state["community"]) if state["community"] else "—"
    e.add_field(name=f"{tr(uid, gid, 'pk_stage')} ({stage_ru})", value=board, inline=False)

    e.add_field(name=tr(uid, gid, "pk_stack"), value=f"`{stack}`", inline=True)
    e.add_field(name=tr(uid, gid, "pk_bet"), value=f"`{my_bet}`", inline=True)
    e.add_field(name=tr(uid, gid, "pk_to_call"), value=f"`{to_call}`", inline=True)
    e.add_field(name=tr(uid, gid, "pk_pot"), value=f"`{state['pot']}`", inline=True)
    if is_current:
        e.set_footer(text=tr(uid, gid, "pk_your_turn").format(state['turn_time']))
    else:
        e.set_footer(text=tr(uid, gid, "pk_waiting_turn"))

    view = ПКХодView(uid, state) if is_current else None

    try:
        user = bot.get_user(uid)
        if user is None:
            user = await bot.fetch_user(uid)
        await user.send(embed=e, view=view)
    except Exception as ex:
        log.error(f"DM не ушло игроку {uid}: {ex}")
        try:
            ch = bot.get_channel(state["thread_id"])
            if ch:
                # ФИКС: не отправляем embed с картами в общий канал
                if view is not None:
                    await ch.send(f"<@{uid}>, {tr(uid, gid, 'pk_dm_fail')}", view=view)
                else:
                    await ch.send(f"<@{uid}>, {tr(uid, gid, 'pk_dm_fail')}")
        except Exception as ex2:
            log.error(f"Fallback тоже упал: {ex2}")

    if is_current:
        mid = state["public_msg_id"]
        old = _покер_таймеры.get(mid)
        cur_task = asyncio.current_task()
        if old and not old.done() and old is not cur_task:
            old.cancel()
        _покер_таймеры[mid] = asyncio.create_task(_пк_таймер(state, uid))


async def _пк_таймер(state, uid):
    try:
        await asyncio.sleep(state["turn_time"])
    except asyncio.CancelledError:
        return
    if state.get("finished"): return
    if state["players"][state["current_idx"]] != uid: return
    if uid in state["folded"]: return
    state["folded"].add(uid)
    gid = state.get("gid", 0)
    await _пк_обновить(state, tr(uid, gid, "pk_auto_fold").format(uid))
    await _пк_продолжить_без(state)


async def _пк_продолжить_без(state):
    активные = [p for p in state["players"] if p not in state["folded"]]
    if len(активные) <= 1:
        await _пк_финал(state, "Авто-фолд"); return
    next_idx = _пк_след_игрок(state, state["current_idx"])
    if next_idx is None or _пк_раунд_закрыт(state):
        await _пк_след_улица_без(state); return
    state["current_idx"] = next_idx
    nxt = state["players"][next_idx]
    await _пк_обновить(state)
    await _пк_эфе_ход(state, nxt)


class МодалкаРейза(Modal):
    def __init__(self, uid, state, view_ref):
        my = state["bets"][uid]
        stack = state["stacks"][uid]
        min_total = state["current_bet"] + state["min_raise"]
        max_total = my + stack
        super().__init__(title=tr(uid, state.get("gid", 0), "pk_modal_raise"))
        self.uid = uid
        self.state = state
        self.view_ref = view_ref
        self.add_item(InputText(
            label=f"Сумма (мин {min_total}, макс {max_total})",
            placeholder=str(min_total),
            style=discord.InputTextStyle.short, required=True))

    async def callback(self, interaction):
        uid = self.uid; s = self.state; gid = s.get("gid", 0)
        try:
            amount = int(self.children[0].value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Число.", ephemeral=True); return
        my = s["bets"][uid]; stack = s["stacks"][uid]
        min_total = s["current_bet"] + s["min_raise"]
        max_total = my + stack
        if amount < min_total:
            await interaction.response.send_message(
                f"❌ Минимум {min_total}.", ephemeral=True); return
        if amount > max_total:
            await interaction.response.send_message(
                f"❌ Максимум {max_total}.", ephemeral=True); return

        t = _покер_таймеры.get(s["public_msg_id"])
        cur_task = asyncio.current_task()
        if t and not t.done() and t is not cur_task:
            t.cancel()

        old_bet = s["current_bet"]  # ФИКС: запоминаем ставку до рейза
        need = amount - my
        s["stacks"][uid] -= need
        s["bets"][uid] = amount
        s["pot"] += need
        s["contributed"][uid] += need
        if s["stacks"][uid] == 0:
            s["all_in"].add(uid)
        
        s["current_bet"] = amount
        s["min_raise"] = max(s["min_raise"], amount - old_bet)  # ФИКС: правильный min_raise
        s["last_raiser_idx"] = s["current_idx"]
        s["acted"] = {uid}

        await interaction.response.send_message(
            f"🔥 Поднял до {amount}", ephemeral=True)
        await _пк_продолжить(s, tr(uid, gid, "pk_raised").format(uid, amount))


class ПКХодView(View):
    def __init__(self, uid, state):
        super().__init__(timeout=state["turn_time"] + 60)
        self.uid = uid; self.state = state; self._rebuild()

    def _rebuild(self):
        self.clear_items()
        s = self.state; uid = self.uid
        my_bet = s["bets"][uid]; to_call = max(0, s["current_bet"] - my_bet)
        stack = s["stacks"][uid]

        gid = s.get("gid", 0)
        fold = Button(label=tr(uid, gid, "pk_btn_fold"),
                      style=discord.ButtonStyle.danger,
                      emoji="❌", custom_id=f"pkh_f_{uid}")
        fold.callback = self._fold; self.add_item(fold)

        if to_call == 0:
            chk = Button(label=tr(uid, gid, "pk_btn_check"),
                         style=discord.ButtonStyle.success,
                         emoji="✅", custom_id=f"pkh_c_{uid}")
            chk.callback = self._check; self.add_item(chk)
        else:
            call = Button(label=tr(uid, gid, "pk_btn_call", n=min(to_call, stack)),
                          style=discord.ButtonStyle.primary, emoji="💵",
                          custom_id=f"pkh_cl_{uid}")
            call.callback = self._call; self.add_item(call)

        if stack > to_call and stack >= (to_call + s["min_raise"]):
            ra = Button(label=tr(uid, gid, "pk_btn_raise"),
                        style=discord.ButtonStyle.primary,
                        emoji="🔥", custom_id=f"pkh_r_{uid}")
            ra.callback = self._open_raise; self.add_item(ra)

        if stack > 0:
            ai = Button(label=tr(uid, gid, "pk_btn_allin", n=stack),
                        style=discord.ButtonStyle.danger, emoji="💀",
                        custom_id=f"pkh_ai_{uid}")
            ai.callback = self._allin; self.add_item(ai)

    def _cancel_timer(self):
        t = _покер_таймеры.get(self.state["public_msg_id"])
        cur_task = asyncio.current_task()
        if t and not t.done() and t is not cur_task:
            t.cancel()

    def _owner(self, i): return i.user.id == self.uid

    async def _fold(self, interaction):
        if not self._owner(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        s = self.state; gid = s.get("gid", 0)
        if s["players"][s["current_idx"]] != self.uid:
            await interaction.response.send_message("❌ Не ваш ход.", ephemeral=True); return
        self._cancel_timer(); s["folded"].add(self.uid)
        s.setdefault("acted", set()).add(self.uid)
        await interaction.response.edit_message(content="❌ Сбросил.", embed=None, view=None)
        await _пк_продолжить(s, tr(self.uid, gid, "pk_folded").format(self.uid))

    async def _check(self, interaction):
        if not self._owner(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        s = self.state; gid = s.get("gid", 0)
        if s["players"][s["current_idx"]] != self.uid:
            await interaction.response.send_message("❌ Не ваш ход.", ephemeral=True); return
        self._cancel_timer()
        s.setdefault("acted", set()).add(self.uid)
        await interaction.response.edit_message(content="✅ Пропустил", embed=None, view=None)
        await _пк_продолжить(s, tr(self.uid, gid, "pk_checked").format(self.uid))

    async def _call(self, interaction):
        if not self._owner(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        s = self.state; gid = s.get("gid", 0)
        if s["players"][s["current_idx"]] != self.uid:
            await interaction.response.send_message("❌ Не ваш ход.", ephemeral=True); return
        self._cancel_timer()
        my = s["bets"][self.uid]; tc = max(0, s["current_bet"] - my)
        amt = min(tc, s["stacks"][self.uid])
        s["stacks"][self.uid] -= amt
        s["bets"][self.uid] += amt
        s["pot"] += amt
        s["contributed"][self.uid] += amt
        if s["stacks"][self.uid] == 0: s["all_in"].add(self.uid)
        s.setdefault("acted", set()).add(self.uid)
        await interaction.response.edit_message(content=f"💵 Уравнял {amt}",
                                                embed=None, view=None)
        await _пк_продолжить(s, tr(self.uid, gid, "pk_called").format(self.uid, amt))

    async def _open_raise(self, interaction):
        if not self._owner(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        s = self.state
        if s["players"][s["current_idx"]] != self.uid:
            await interaction.response.send_message("❌ Не ваш ход.", ephemeral=True); return
        await interaction.response.send_modal(МодалкаРейза(self.uid, s, self))

    async def _allin(self, interaction):
        if not self._owner(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        s = self.state; gid = s.get("gid", 0)
        if s["players"][s["current_idx"]] != self.uid:
            await interaction.response.send_message("❌ Не ваш ход.", ephemeral=True); return
        self._cancel_timer()
        stack = s["stacks"][self.uid]
        if stack <= 0:
            await interaction.response.send_message("❌ Стек пуст.", ephemeral=True); return
        my = s["bets"][self.uid]
        new_total = my + stack
        old_bet = s["current_bet"]
        s["stacks"][self.uid] = 0
        s["bets"][self.uid] = new_total
        s["pot"] += stack
        s["contributed"][self.uid] += stack
        s["all_in"].add(self.uid)
        if new_total > s["current_bet"]:
            s["current_bet"] = new_total
            s["min_raise"] = max(s["min_raise"], new_total - old_bet) # ФИКС
            s["last_raiser_idx"] = s["current_idx"]
        s.setdefault("acted", set()).add(self.uid)
        await interaction.response.edit_message(
            content=f"💀 ВА-БАНК {stack}", embed=None, view=None)
        await _пк_продолжить(s, tr(self.uid, gid, "pk_allin").format(self.uid, stack))


def _пк_след_игрок(state, start_idx):
    n = len(state["players"])
    for i in range(1, n+1):
        idx = (start_idx+i) % n; uid = state["players"][idx]
        if uid in state["folded"] or uid in state["all_in"]: continue
        return idx
    return None


def _пк_раунд_закрыт(state):
    активные = [p for p in state["players"] if p not in state["folded"]]
    if len(активные) <= 1: return True
    acted = state.get("acted", set())
    for uid in активные:
        if uid in state["all_in"]: continue
        if uid not in acted: return False
        if state["bets"][uid] != state["current_bet"]: return False
    return True


async def _пк_продолжить(state, log_line):
    await _пк_обновить(state, log_line)
    _покер_сохранить()
    активные = [p for p in state["players"] if p not in state["folded"]]
    if len(активные) <= 1:
        await _пк_финал(state, "Все сбросили"); return

    if all(u in state["all_in"] for u in активные):
        await _пк_след_улица(state)
        return

    next_idx = _пк_след_игрок(state, state["current_idx"])
    if next_idx is None or _пк_раунд_закрыт(state):
        await _пк_след_улица(state); return
    state["current_idx"] = next_idx
    nxt = state["players"][next_idx]
    await _пк_обновить(state)
    await _пк_эфе_ход(state, nxt)


async def _пк_след_улица(state):
    gid = state.get("gid", 0)
    активные_не_фолд = [u for u in state["players"] if u not in state["folded"]]
    if len(активные_не_фолд) >= 2 and all(u in state["all_in"] for u in активные_не_фолд):
        while state["stage"] != "river":
            if state["stage"] == "preflop":
                state["community"] += [state["deck"].pop() for _ in range(3)]
                state["stage"] = "flop"
            elif state["stage"] == "flop":
                state["community"].append(state["deck"].pop()); state["stage"] = "turn"
            elif state["stage"] == "turn":
                state["community"].append(state["deck"].pop()); state["stage"] = "river"
        await _пк_обновить(state, tr(gid, gid, "pk_allin_showdown"))
        await _пк_финал(state, "Все ALL-IN")
        return

    if state["stage"] == "preflop":
        state["community"] += [state["deck"].pop() for _ in range(3)]
        state["stage"] = "flop"
    elif state["stage"] == "flop":
        state["community"].append(state["deck"].pop()); state["stage"] = "turn"
    elif state["stage"] == "turn":
        state["community"].append(state["deck"].pop()); state["stage"] = "river"
    elif state["stage"] == "river":
        await _пк_финал(state, "Showdown"); return

    for uid in state["players"]: state["bets"][uid] = 0
    state["current_bet"] = 0; state["min_raise"] = state["bb"]
    state["acted"] = set()

    n = len(state["players"]); idx = (state["dealer_idx"]+1) % n
    for _ in range(n):
        uid = state["players"][idx]
        if uid not in state["folded"] and uid not in state["all_in"]: break
        idx = (idx+1) % n
    state["current_idx"] = idx
    first = state["players"][idx]
    stage_name = {"flop":"Flop","turn":"Тёрн","river":"Ривер"}.get(state["stage"], state["stage"])
    await _пк_обновить(state, tr(gid, gid, "pk_stage_bets").format(stage_name))
    await _пк_эфе_ход(state, first)


async def _пк_след_улица_без(state):
    gid = state.get("gid", 0)
    активные_не_фолд = [u for u in state["players"] if u not in state["folded"]]
    if len(активные_не_фолд) >= 2 and all(u in state["all_in"] for u in активные_не_фолд):
        while state["stage"] != "river":
            if state["stage"] == "preflop":
                state["community"] += [state["deck"].pop() for _ in range(3)]
                state["stage"] = "flop"
            elif state["stage"] == "flop":
                state["community"].append(state["deck"].pop()); state["stage"] = "turn"
            elif state["stage"] == "turn":
                state["community"].append(state["deck"].pop()); state["stage"] = "river"
        await _пк_обновить(state, tr(gid, gid, "pk_allin_showdown"))
        await _пк_финал(state, "Все ALL-IN")
        return

    if state["stage"] == "preflop":
        state["community"] += [state["deck"].pop() for _ in range(3)]
        state["stage"] = "flop"
    elif state["stage"] == "flop":
        state["community"].append(state["deck"].pop()); state["stage"] = "turn"
    elif state["stage"] == "turn":
        state["community"].append(state["deck"].pop()); state["stage"] = "river"
    elif state["stage"] == "river":
        await _пк_финал(state, "Showdown"); return

    for uid in state["players"]: state["bets"][uid] = 0
    state["current_bet"] = 0; state["min_raise"] = state["bb"]
    state["acted"] = set()
    n = len(state["players"]); idx = (state["dealer_idx"]+1) % n
    for _ in range(n):
        uid = state["players"][idx]
        if uid not in state["folded"] and uid not in state["all_in"]: break
        idx = (idx+1) % n
    state["current_idx"] = idx
    await _пк_обновить(state, tr(gid, gid, "pk_stage_bets").format(state['stage'].capitalize()))
    await _пк_эфе_ход(state, state["players"][idx])


async def _пк_обновить(state, log_line=None):
    if not state.get("public_msg_id"): return
    try:
        ch = bot.get_channel(state["thread_id"])
        if not ch: return
        msg = await ch.fetch_message(state["public_msg_id"])
        e = _пк_рендер(state)
        if log_line: e.add_field(name="📝", value=log_line, inline=False)
        await msg.edit(embed=e)
    except Exception as ex:
        log.warning(f"Публичный не обновился: {ex}")


async def _пк_финал(state, reason):
    state["finished"] = True; state["stage"] = "showdown"

    cur_task = asyncio.current_task()
    t = _покер_таймеры.pop(state["public_msg_id"], None)
    if t and not t.done() and t is not cur_task:
        t.cancel()

    активные = [p for p in state["players"] if p not in state["folded"]]

    scores = {}
    if len(активные) > 1:
        for uid in активные:
            scores[uid] = _пк_оценить(state["hole"][uid] + state["community"])

    выплаты = defaultdict(int)
    банки = _пк_разбить_банк(state)

    for сумма, претенденты in банки:
        if not претенденты:
            continue
        if len(претенденты) == 1:
            выплаты[претенденты[0]] += сумма
            continue
        best = max(претенденты, key=lambda u: scores.get(u, (0, (), ""))[:2])
        best_sc = scores.get(best, (0, (), ""))
        ties = [u for u in претенденты if scores.get(u, (0,(),""))[:2] == best_sc[:2]]
        доля = сумма // len(ties)
        for u in ties:
            выплаты[u] += доля
        остаток = сумма - доля * len(ties)
        if остаток:
            выплаты[ties[0]] += остаток

    for uid, сумма in выплаты.items():
        st = получить_статы(state["gid"], uid)
        st["coins"] += сумма
        if сумма > 0:
            st["missions"]["casino_wins"] = st["missions"].get("casino_wins", 0) + 1
            st["xp"] += 150
            if isinstance(bot.get_user(uid), discord.User):
                member = bot.get_guild(state["gid"]).get_member(uid) if bot.get_guild(state["gid"]) else None
                if member:
                    asyncio.create_task(проверить_роли(member, st["xp"], st["rank_override"]))
    сохранить_данные()

    gid = state.get("gid", 0)
    e = _пк_рендер(state, reveal=True)
    if len(активные) == 1:
        e.add_field(name=tr(gid, gid, "pk_winner"),
                    value=tr(gid, gid, "pk_wins_pot").format(активные[0], state['pot'], reason),
                    inline=False)
    else:
        lines = [f"<@{uid}> — {_пк_карты(state['hole'][uid])} → **{scores[uid][2]}**"
                 for uid in активные]
        winners = [u for u, s in выплаты.items() if s > 0]
        if len(winners) == 1:
            e.add_field(name=tr(gid, gid, "pk_winner"),
                        value=tr(gid, gid, "pk_takes_pot").format(winners[0]) + "\n" + "\n".join(lines),
                        inline=False)
        else:
            ts = ", ".join(f"<@{u}>" for u in winners)
            e.add_field(name=tr(gid, gid, "pk_split"),
                        value=f"{ts}\n" + "\n".join(lines),
                        inline=False)

    try:
        ch = bot.get_channel(state["thread_id"])
        if ch:
            msg = await ch.fetch_message(state["public_msg_id"])
            await msg.edit(embed=e, view=None)
            await ch.send(tr(gid, gid, "pk_closing"))
    except Exception as ex:
        log.warning(f"Финал не отобразился: {ex}")
    finally:
        _покер_толы.pop(state["public_msg_id"], None)
        _покер_сохранить()
        # ФИКС: передаем ID лобби-сообщения для удаления
        asyncio.create_task(_пк_удалить_ветку(
            state["thread_id"], 5, 
            state.get("parent_channel_id"), 
            state.get("parent_msg_id")))


async def _пк_удалить_ветку(thread_id, minutes=5, parent_channel_id=None, parent_msg_id=None):
    await asyncio.sleep(minutes*60)
    
    # Удаляем лобби-сообщение
    if parent_channel_id and parent_msg_id:
        try:
            ch = bot.get_channel(parent_channel_id) or await bot.fetch_channel(parent_channel_id)
            msg = await ch.fetch_message(parent_msg_id)
            await msg.delete()
            log.info(f"Лобби-сообщение покера {parent_msg_id} удалено")
        except discord.NotFound:
            pass
        except Exception as e:
            log.warning(f"Не удалил лобби-сообщение: {e}")

    # Удаляем ветку
    try:
        ch = bot.get_channel(thread_id) or await bot.fetch_channel(thread_id)
        await ch.delete()
        log.info(f"Ветка покера {thread_id} удалена")
    except discord.NotFound: pass
    except Exception as e: log.warning(f"Не удалил ветку: {e}")


# ============================================================
# БЛЭКДЖЕК
# ============================================================
_бдж_активные: dict[tuple[int, int], dict] = {}

_БДЖ_МАСТИ = ["♠️", "♥️", "♦️", "♣️"]
_БДЖ_РАНГИ = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def _бдж_колода():
    d = [(r, s) for s in _БДЖ_МАСТИ for r in _БДЖ_РАНГИ]
    random.shuffle(d); return d


def _бдж_карта(c): return f"`{c[0]}{c[1]}`"


def _бдж_рука(cards, hidden=False):
    if not cards: return "—"
    if hidden: return f"{_бдж_карта(cards[0])}  🎴"
    return "  ".join(_бдж_карта(c) for c in cards)


def _бдж_значение(cards):
    total, aces = 0, 0
    for r, s in cards:
        if r == "A": aces += 1; total += 11
        elif r in ("K", "Q", "J", "10"): total += 10
        else: total += int(r)
    while total > 21 and aces > 0:
        total -= 10; aces -= 1
    return total


def _бдж_блэкджек(cards):
    return len(cards) == 2 and _бдж_значение(cards) == 21


class БДЖПротивБота(View):
    def __init__(self, uid, gid, bet, player, dealer, deck):
        super().__init__(timeout=180)
        self.uid = uid; self.gid = gid; self.bet = bet
        self.player = player; self.dealer = dealer; self.deck = deck

    def _эмбед(self, log=""):
        pv = _бдж_значение(self.player)
        dv = _бдж_значение(self.dealer[:1])
        e = discord.Embed(title=tr(self.uid, self.gid, "bj_title"),
                          color=discord.Color.dark_green())
        e.add_field(name=tr(self.uid, self.gid, "bj_your_cards"),
                    value=f"{_бдж_рука(self.player)}  ({tr(self.uid, self.gid, 'bj_sum')}: **{pv}**)",
                    inline=False)
        e.add_field(name=tr(self.uid, self.gid, "bj_dealer"),
                    value=f"{_бдж_рука(self.dealer, hidden=True)}  ({tr(self.uid, self.gid, 'bj_visible')}: **{dv}**)",
                    inline=False)
        e.add_field(name=tr(self.uid, self.gid, "bj_bet"), value=f"`{self.bet}`", inline=True)
        if log: e.add_field(name="📝", value=log, inline=False)
        return e

    async def _owner(self, interaction):
        if interaction.user.id != self.uid:
            await interaction.response.send_message(tr(self.uid, self.gid, "bj_not_yours"), ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success, emoji="➕")
    async def hit(self, button, interaction):
        if not await self._owner(interaction): return
        self.player.append(self.deck.pop())
        if _бдж_значение(self.player) > 21:
            _бдж_активные.pop((self.gid, self.uid), None)
            await interaction.response.edit_message(
                embed=self._эмбед(tr(self.uid, self.gid, "bj_bust").format(self.bet)),
                view=None)
            return
        await interaction.response.edit_message(embed=self._эмбед(tr(self.uid, self.gid, "bj_drew")),
                                                view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.primary, emoji="✋")
    async def stand(self, button, interaction):
        if not await self._owner(interaction): return
        while _бдж_значение(self.dealer) < 17:
            self.dealer.append(self.deck.pop())
        pv = _бдж_значение(self.player); dv = _бдж_значение(self.dealer)
        st = получить_статы(self.gid, self.uid)
        p_bj = _бдж_блэкджек(self.player); d_bj = _бдж_блэкджек(self.dealer)
        gid = self.gid; uid = self.uid

        if p_bj and not d_bj:
            win = int(self.bet * 1.5); st["coins"] += self.bet + win
            log = tr(uid, gid, "bj_blackjack").format(win)
        elif d_bj and not p_bj:
            log = tr(uid, gid, "bj_dealer_bj").format(self.bet)
        elif dv > 21:
            st["coins"] += self.bet * 2
            log = tr(uid, gid, "bj_dealer_bust").format(self.bet)
        elif pv > dv:
            st["coins"] += self.bet * 2
            log = tr(uid, gid, "bj_win").format(self.bet)
        elif dv > pv:
            log = tr(uid, gid, "bj_lose").format(self.bet)
        else:
            st["coins"] += self.bet
            log = tr(uid, gid, "bj_draw").format(self.bet)

        сохранить_данные()
        _бдж_активные.pop((self.gid, self.uid), None)

        e = discord.Embed(title=tr(uid, gid, "bj_result_title"),
                          color=discord.Color.dark_green())
        e.add_field(name=tr(uid, gid, "bj_you"), value=f"{_бдж_рука(self.player)} → **{pv}**", inline=False)
        e.add_field(name=tr(uid, gid, "bj_dealer"), value=f"{_бдж_рука(self.dealer)} → **{dv}**",
                    inline=False)
        e.add_field(name="📝", value=log, inline=False)
        await interaction.response.edit_message(embed=e, view=None)


# ============================================================
# СЛЭШ-КОМАНДЫ
# ============================================================
@bot.slash_command(name="don", description="Don's office / Кабинет Дона")
async def cmd_don(ctx: discord.ApplicationContext):
    await ctx.respond(
        tr(ctx.author.id, ctx.guild.id, "don_welcome",
           bot=ИМЯ_БОТА, family=ИМЯ_СЕМЬИ),
        view=ГлавнаяПанель(), ephemeral=True)


@bot.slash_command(name="lang", description="Change language / Сменить язык")
async def cmd_lang(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    cur = st.get("lang", ЯЗЫК_ПО_УМОЛЧАНИЮ)
    cur_label = ЯЗЫКИ.get(cur, cur)

    opts = [discord.SelectOption(label=ЯЗЫКИ[c], value=c,
                                 emoji="🇬🇧" if c == "en" else "🇷🇺")
            for c in ЯЗЫКИ]
    sel = Select(placeholder="🌐 Language / Язык", options=opts)

    async def on_pick(interaction: discord.Interaction):
        chosen = interaction.data["values"][0]
        if chosen not in ЯЗЫКИ: return
        s = получить_статы(interaction.guild.id, interaction.user.id)
        s["lang"] = chosen
        сохранить_данные()
        await interaction.response.edit_message(
            content=tr(interaction.user.id, interaction.guild.id, "lang_changed",
                       lang=ЯЗЫКИ[chosen]), view=None)

    sel.callback = on_pick
    view = View(timeout=120)
    view.add_item(sel)

    text = tr(uid, gid, "lang_title") + "\n\n" + tr(uid, gid, "lang_current",
                                                     lang=cur_label)
    await ctx.respond(text, view=view, ephemeral=True)


@bot.slash_command(name="wallet", description="Wallet / Кошелёк")
async def cmd_wallet(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    embed = discord.Embed(title=tr(uid, gid, "wallet_title"),
                          description=tr(uid, gid, "wallet_have", amount=st["coins"]),
                          color=discord.Color.dark_gold())
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="daily", description="Collect tribute / Собрать дань")
async def cmd_daily(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    now = time.time()
    last = st.get("last_daily_time", 0)
    streak = st.get("streak_days", 0)
    if now - last < КД_ДЕЙЛИ:
        rem = КД_ДЕЙЛИ - (now - last)
        h = int(rem // 3600); m = int((rem % 3600) // 60)
        await ctx.respond(tr(uid, gid, "daily_cooldown", h=h, m=m, streak=streak),
                          ephemeral=True)
        return
    if now - last > СБРОС_ДЕЙЛИ: streak = 0
    streak += 1
    mult = min(streak, МАКС_МНОЖИТЕЛЬ)
    reward = НАГРАДА_ДЕЙЛИ + БОНУС_STREAK * (streak - 1)
    st["coins"] += reward
    st["last_daily_time"] = now
    st["streak_days"] = streak
    st["missions"]["daily_claimed"] = 1
    сохранить_данные()
    embed = discord.Embed(
        title=tr(uid, gid, "daily_title"),
        description=(f"{tr(uid, gid, 'daily_got')}: **+{reward}** 💰\n"
                     f"{tr(uid, gid, 'daily_streak')}: **{streak}** (x{mult})\n"
                     f"{tr(uid, gid, 'daily_next')}\n"
                     f"{tr(uid, gid, 'daily_hint')}"),
        color=discord.Color.dark_gold())
    await ctx.respond(embed=embed)


@bot.slash_command(name="casino", description="Underground casino / Казино")
async def cmd_casino(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    await ctx.respond(
        f"{tr(uid, gid, 'casino_opened', user=ctx.author.mention)}\n\n"
        f"{tr(uid, gid, 'casino_wallet')}: **{st['coins']}** 💰\n\n"
        f"{tr(uid, gid, 'casino_pick')}",
        view=ПанельКазино(uid))


@bot.slash_command(name="missions", description="Family business / Дела семьи")
async def cmd_missions(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    сбросить_миссии(st)
    m = st["missions"]
    claimed = m["claimed"]

    def s(k, tgt, cur):
        if k in claimed: return tr(uid, gid, "m_claimed")
        if cur >= tgt: return tr(uid, gid, "m_ready")
        return f"`{прогресс_бар(cur / tgt, 8)}` {cur}/{tgt}"

    desc = (
        f"{tr(uid, gid, 'm_l1')}: {s('msg', 5, m.get('msg_count', 0))}\n"
        f"{tr(uid, gid, 'm_l2')}: {s('media', 3, m.get('media_count', 0))}\n"
        f"{tr(uid, gid, 'm_l3')}: {s('casino', 3, m.get('casino_played', 0))}\n"
        f"{tr(uid, gid, 'm_l4')}: {s('casino_win', 3, m.get('casino_wins', 0))}\n"
        f"{tr(uid, gid, 'm_l5')}: {s('duel_win', 1, m.get('duel_wins', 0))}\n"
        f"{tr(uid, gid, 'm_l6')}: {s('transfer', 1, m.get('transfer_sent', 0))}\n"
        f"{tr(uid, gid, 'm_l7')}: {s('shop', 1, m.get('shop_bought', 0))}\n"
        f"{tr(uid, gid, 'm_l8')}: {s('poll', 1, m.get('poll_voted', 0))}\n"
        f"{tr(uid, gid, 'm_l9')}: {s('roll', 1, m.get('roll_high', 0))}\n"
        f"{tr(uid, gid, 'm_l10')}: {s('daily', 1, m.get('daily_claimed', 0))}\n"
        f"{tr(uid, gid, 'm_l11')}: {s('furry', 1, m.get('furry_triggered', 0))}\n"
        f"{tr(uid, gid, 'm_l12')}: {s('hardcore', 10000, st['xp'])}"
    )
    embed = discord.Embed(title=tr(uid, gid, "m_title"),
                          description=desc,
                          color=discord.Color.dark_gold(),
                          timestamp=datetime.now(timezone.utc))
    embed.set_footer(text=tr(uid, gid, "m_footer"))
    await ctx.respond(embed=embed, view=ПанельМиссий(uid, gid), ephemeral=True)


@bot.slash_command(name="achievements", description="Achievements / Достижения")
async def cmd_ach(ctx: discord.ApplicationContext,
                  member: discord.Member | None = None):
    target = member or ctx.author
    uid = target.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    have = set(st.get("achievements", []))
    lines = []
    for key, ach in ДОСТИЖЕНИЯ.items():
        icon = tr(uid, gid, "ach_unlocked") if key in have else tr(uid, gid, "ach_locked")
        name = tr(uid, gid, ach["name_key"])
        desc = tr(uid, gid, ach["desc_key"])
        lines.append(f"{icon} **{name}** — `+{ach['xp']} XP`\n   *{desc}*")
    embed = discord.Embed(
        title=tr(uid, gid, "ach_title_own", name=target.display_name),
        description="\n\n".join(lines) + "\n\n" +
                    tr(uid, gid, "ach_total", have=len(have), total=len(ДОСТИЖЕНИЯ)),
        color=discord.Color.gold(),
        timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="top", description="Family registry / Реестр семьи")
async def cmd_top(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, "Category / Категория",
                             choices=["XP", "Money", "Casino", "Messages"],
                             default="XP") = "XP",
):
    uid = ctx.author.id; gid = ctx.guild.id
    if gid not in данные_юзеров or not данные_юзеров[gid]:
        await ctx.respond(tr(uid, gid, "top_empty"), ephemeral=True)
        return
    if category == "XP":
        kf = lambda x: x[1]["xp"]; cat_label = tr(uid, gid, "top_xp")
    elif category == "Money":
        kf = lambda x: x[1]["coins"]; cat_label = tr(uid, gid, "top_money")
    elif category == "Casino":
        kf = lambda x: x[1]["missions"]["casino_played"]; cat_label = tr(uid, gid, "top_casino")
    else:
        kf = lambda x: x[1]["missions"]["msg_count"]; cat_label = tr(uid, gid, "top_msgs")

    srt = sorted(данные_юзеров[gid].items(), key=kf, reverse=True)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    desc = ""
    for i, (u_id, stats) in enumerate(srt[:10], 1):
        member = ctx.guild.get_member(u_id)
        name = member.name if member else f"ID: {u_id}"
        prefix = medals.get(i, f"`{i}.`")
        if category == "XP":
            val = f"`{stats['xp']} XP`"
        elif category == "Money":
            val = f"`{stats['coins']} 💰`"
        elif category == "Casino":
            val = f"`{stats['missions']['casino_played']}`"
        else:
            val = f"`{stats['missions']['msg_count']}`"
        desc += f"{prefix} **{name}** — {val}\n"
    embed = discord.Embed(title=tr(uid, gid, "top_title", cat=cat_label),
                          description=desc,
                          color=discord.Color.dark_gold(),
                          timestamp=datetime.now(timezone.utc))
    await ctx.respond(embed=embed)


@bot.slash_command(name="verify", description="Verify Roblox / Verifica Roblox")
async def cmd_verify(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    if st.get("verified"):
        await ctx.respond(tr(uid, gid, "ver_already", nick=st.get("roblox_username")),
                          ephemeral=True)
        return
    await ctx.send_modal(МодалкаВерификации(uid, gid))


@bot.slash_command(name="whois", description="Roblox profile / Roblox-профиль")
async def cmd_whois(ctx: discord.ApplicationContext, member: discord.Member):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, member.id)
    if not st.get("verified"):
        await ctx.respond(f"❌ {member.mention} — not verified / не верифицирован.",
                          ephemeral=True)
        return
    embed = discord.Embed(
        title=f"Roblox: {member.display_name}",
        description=(f"**Username:** {st['roblox_username']}\n"
                     f"**ID:** `{st['roblox_id']}`\n"
                     f"[Open profile](https://www.roblox.com/users/{st['roblox_id']}/profile)"),
        color=discord.Color.dark_gold())
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.respond(embed=embed)


@bot.slash_command(name="transfer", description="Transfer money / Передать деньги")
async def cmd_transfer(ctx: discord.ApplicationContext,
                       member: discord.Member, amount: int):
    uid = ctx.author.id; gid = ctx.guild.id
    if member.bot:
        await ctx.respond(tr(uid, gid, "err_bot"), ephemeral=True); return
    if member.id == uid:
        await ctx.respond(tr(uid, gid, "err_self"), ephemeral=True); return
    if amount <= 0:
        await ctx.respond(tr(uid, gid, "give_positive"), ephemeral=True); return
    rem = кд_перевода_ок(gid, uid)
    if rem > 0:
        await ctx.respond(tr(uid, gid, "tr_cd", sec=rem), ephemeral=True); return
    snd = получить_статы(gid, uid)
    rcv = получить_статы(gid, member.id)
    if snd["coins"] < amount:
        await ctx.respond(tr(uid, gid, "tr_no_money", balance=snd["coins"]),
                          ephemeral=True)
        return
    snd["coins"] -= amount
    rcv["coins"] += amount
    snd["missions"]["transfer_sent"] = snd["missions"].get("transfer_sent", 0) + 1
    сохранить_данные()
    await ctx.respond(tr(uid, gid, "tr_ok", sender=ctx.author.mention,
                         receiver=member.mention, amount=amount))


@bot.slash_command(name="profile", description="Profile / Досье")
async def cmd_profile(ctx: discord.ApplicationContext,
                      member: discord.Member | None = None):
    target = member or ctx.author
    st = получить_статы(ctx.guild.id, target.id)
    await ctx.respond(
        embed=эмбед_профиля(st, target),
        view=ПрофильКнопки(user_id=target.id) if member else ПрофильКнопки())


@bot.slash_command(name="roll", description="Roll dice / Бросить кости")
async def cmd_roll(
    ctx: discord.ApplicationContext,
    maximum: discord.Option(int, "Maximum", min_value=2, max_value=10000) = 100,
):
    uid = ctx.author.id; gid = ctx.guild.id
    result = random.randint(1, maximum)
    if maximum == 100 and result >= 90:
        st = получить_статы(gid, uid)
        st["missions"]["roll_high"] = 1
        сохранить_данные()
    await ctx.respond(f"🎲 **{ctx.author.mention}** rolls... / бросает кости...\n\n"
                      f"**{result}** / {maximum}")


@bot.slash_command(name="shop", description="Black market / Чёрный рынок")
async def cmd_shop(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    embed = discord.Embed(
        title=tr(uid, gid, "shop_title"),
        description=tr(uid, gid, "shop_wallet", coins=st["coins"]),
        color=discord.Color.dark_gold())
    for key, item in ТОВАРЫ.items():
        desc = tr(uid, gid, item["desc_key"])
        embed.add_field(
            name=f"{item['emoji']} {item['label']} — {item['price']} 💰",
            value=f"*{desc}*", inline=False)
    await ctx.respond(embed=embed, view=ПанельМагазина(uid, gid), ephemeral=True)


@bot.slash_command(name="duel", description="Showdown / Разборка")
async def cmd_duel(ctx: discord.ApplicationContext,
                   member: discord.Member, amount: int):
    uid = ctx.author.id; gid = ctx.guild.id
    if member.bot or member.id == uid:
        await ctx.respond(tr(uid, gid, "duel_bad_target"), ephemeral=True); return
    if amount <= 0:
        await ctx.respond(tr(uid, gid, "duel_bad_bet"), ephemeral=True); return
    ch_st = получить_статы(gid, uid)
    tg_st = получить_статы(gid, member.id)
    if ch_st["coins"] < amount:
        await ctx.respond(tr(uid, gid, "duel_no_money", amount=amount),
                          ephemeral=True); return
    if tg_st["coins"] < amount:
        await ctx.respond(f"❌ {member.mention} — not enough / нет **{amount}** 💰.",
                          ephemeral=True); return
    await ctx.respond(
        tr(uid, gid, "duel_title", ch=ctx.author.mention, tg=member.mention,
           amount=amount),
        view=ПодтверждениеДуэли(uid, member.id, amount, gid))


@bot.slash_command(name="changelog", description="Publish update / Обновление")
async def cmd_changelog(
    ctx: discord.ApplicationContext,
    version: discord.Option(str, "Version", required=True),
    text: discord.Option(str, "What's new", required=True),
):
    uid = ctx.author.id; gid = ctx.guild.id
    if not (ctx.author.guild_permissions.administrator or
            ctx.author.guild_permissions.manage_messages):
        await ctx.respond(tr(uid, gid, "cl_don_only"), ephemeral=True); return
    ch = найти_канал(ctx.guild, КАНАЛ_CHANGELOG)
    if not ch:
        await ctx.respond(tr(uid, gid, "cl_channel_no", ch=КАНАЛ_CHANGELOG),
                          ephemeral=True); return
    s = получить_настройки(gid)
    s["changelog"].append({"version": version, "text": text,
                           "author_id": uid, "ts": time.time()})
    сохранить_настройки()
    embed = discord.Embed(title=tr(uid, gid, "cl_update", v=version),
                          description=text[:4000],
                          color=discord.Color.dark_gold(),
                          timestamp=datetime.now(timezone.utc))
    embed.set_author(name=ctx.author.display_name,
                     icon_url=ctx.author.display_avatar.url)
    await ch.send(embed=embed)
    await ctx.respond(tr(uid, gid, "cl_published", ch=ch.mention), ephemeral=True)


@bot.slash_command(name="bug", description="Bug report / Баг-репорт")
async def cmd_bug(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, "Category / Категория",
                             choices=["Game / Игра", "Server / Сервер"],
                             required=True),
):
    cat = "game" if category.startswith("Game") else "server"
    await ctx.send_modal(МодалкаБага(cat, ctx.author.id, ctx.guild.id))


@bot.slash_command(name="suggest", description="Suggest idea / Предложить идею")
async def cmd_suggest(ctx: discord.ApplicationContext):
    await ctx.send_modal(МодалкаПредложения(ctx.author.id, ctx.guild.id))


@bot.slash_command(name="help", description="Help / Помощь")
async def cmd_help(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    is_admin = ctx.author.guild_permissions.administrator
    embed = discord.Embed(
        title=tr(uid, gid, "help_title", bot=ИМЯ_БОТА),
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc))
    embed.add_field(name=tr(uid, gid, "help_family"),
                    value=("`/don` `/wallet` `/daily` `/casino` `/missions`\n"
                           "`/achievements` `/shop` `/duel` `/transfer`\n"
                           "`/profile` `/top` `/roll` `/lang`\n"
                           "`/ask` `/story` `/bj` `/poker`"),
                    inline=False)
    embed.add_field(name=tr(uid, gid, "help_game"),
                    value=("`/verify` `/whois` `/bug` `/suggest`\n"
                           "`/poll` `/remind` `/setbg`"),
                    inline=False)
    if is_admin:
        embed.add_field(name=tr(uid, gid, "help_mod"),
                        value=("`/warn` `/mute` `/unmute` `/kick`\n"
                               "`/ban` `/unban` `/history` `/automod` `/serverinfo`"),
                        inline=False)
        embed.add_field(name=tr(uid, gid, "help_admin"),
                        value="`/changelog` • `/don` → Don's office",
                        inline=False)
    embed.set_footer(text=tr(uid, gid, "help_footer"))
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="setbg", description="Profile background / Фон профиля")
async def cmd_setbg(ctx: discord.ApplicationContext,
                    url: discord.Option(str, "Image URL", required=True)):
    uid = ctx.author.id; gid = ctx.guild.id
    st = получить_статы(gid, uid)
    if "profile_bg" not in st.get("inventory", []):
        await ctx.respond(tr(uid, gid, "bg_no_slot"), ephemeral=True); return
    if not url.startswith("http"):
        await ctx.respond(tr(uid, gid, "bg_url_bad"), ephemeral=True); return
    st["profile_bg"] = url
    сохранить_данные()
    await ctx.respond(tr(uid, gid, "bg_ok"), ephemeral=True)


@bot.slash_command(name="poll", description="Create poll / Опрос")
async def cmd_poll(
    ctx: discord.ApplicationContext,
    question: discord.Option(str, "Question / Вопрос", required=True),
    option1: discord.Option(str, "Option 1", required=True),
    option2: discord.Option(str, "Option 2", required=True),
    option3: discord.Option(str, "Option 3", required=False, default=None),
    option4: discord.Option(str, "Option 4", required=False, default=None),
):
    uid = ctx.author.id; gid = ctx.guild.id
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    embed = discord.Embed(title=f"📊 {question}",
                          color=discord.Color.dark_gold(),
                          timestamp=datetime.now(timezone.utc))
    embed.description = "\n".join(f"{numbers[i]} {o}" for i, o in enumerate(options))
    embed.set_footer(text=f"{tr(uid, gid, 'poll_author')}: {ctx.author.display_name}")
    msg = await ctx.respond(embed=embed, view=КнопкаЗакрытияОпроса())
    sent = await msg.original_response()
    for i in range(len(options)):
        try:
            await sent.add_reaction(numbers[i])
        except Exception:
            pass


class МодалкаНапоминания(Modal):
    def __init__(self, sec: int, uid: int, gid: int):
        super().__init__(title=tr(uid, gid, "rem_t"))
        self.sec = sec
        self.add_item(InputText(label=tr(uid, gid, "rem_what"),
                                placeholder=tr(uid, gid, "rem_ph"),
                                style=discord.InputTextStyle.short,
                                required=True, max_length=200))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        text = self.children[0].value.strip()
        await interaction.response.send_message(
            tr(uid, gid, "rem_set", dur=человеческое_время(self.sec), text=text),
            ephemeral=True)
        await asyncio.sleep(self.sec)
        try:
            await interaction.user.send(
                tr(uid, gid, "rem_dm", text=text, guild=interaction.guild.name))
        except Exception:
            try:
                await interaction.channel.send(
                    tr(uid, gid, "rem_channel", user=interaction.user.mention,
                       text=text))
            except Exception:
                pass


@bot.slash_command(name="remind", description="Reminder / Напоминание")
async def cmd_remind(
    ctx: discord.ApplicationContext,
    time_str: discord.Option(str, "30s / 5m / 2h / 1d", required=True),
):
    uid = ctx.author.id; gid = ctx.guild.id
    sec = парсить_время(time_str)
    if not sec or sec < 10:
        await ctx.respond(tr(uid, gid, "err_bad_time"), ephemeral=True); return
    if sec > 7 * 86400:
        await ctx.respond(tr(uid, gid, "err_max_7d"), ephemeral=True); return
    await ctx.send_modal(МодалкаНапоминания(sec, uid, gid))


def _мп():
    return discord.Permissions(manage_messages=True)


async def _сим_блок(ctx: discord.ApplicationContext) -> bool:
    if выключено(ctx.guild.id, "mod_commands"):
        bot_top = ctx.guild.get_member(bot.user.id).top_role
        await ctx.respond(
            f"❌ **Command failed** for {ctx.author.mention}\n\n"
            f"Bot **cannot perform this action** — permissions insufficient.\n\n"
            f"**Error:** `403 Forbidden` — Missing Permissions\n"
            f"**Error code:** `50013`\n"
            f"**Reason:** bot's role is not high enough in the hierarchy.\n"
            f"**Bot top role:** `{bot_top.name}` (`{bot_top.position}`)\n"
            f"**Fix:** raise the bot's role above the target's role.",
            ephemeral=True)
        return True
    return False


@bot.slash_command(name="warn", description="Warn / Attenzione",
                   default_member_permissions=_мп())
async def cmd_warn(
    ctx: discord.ApplicationContext,
    member: discord.Member,
    reason: discord.Option(str, "Reason / Причина", required=True),
):
    if await _сим_блок(ctx): return
    uid = ctx.author.id; gid = ctx.guild.id
    if member.bot or member.id == uid:
        await ctx.respond("❌", ephemeral=True); return
    добавить_наказание(gid, member.id, "warn", reason, uid)
    try:
        await member.send(tr(member.id, gid, "warn_dm",
                             guild=ctx.guild.name, reason=reason))
    except Exception:
        pass
    await ctx.respond(tr(uid, gid, "warn_done", user=member.mention, reason=reason))
    await лог_админа(ctx.guild, ctx.author, "Attenzione",
                     f"{member.mention} (`{member.id}`)\nReason: {reason}")


@bot.slash_command(name="mute", description="Silenzio (mute)",
                   default_member_permissions=_мп())
async def cmd_mute(
    ctx: discord.ApplicationContext,
    member: discord.Member,
    time_str: discord.Option(str, "5m / 1h / 1d", required=True),
    reason: discord.Option(str, "Reason / Причина", required=True, default="—"),
):
    if await _сим_блок(ctx): return
    uid = ctx.author.id; gid = ctx.guild.id
    if member.bot or member.id == uid:
        await ctx.respond("❌", ephemeral=True); return
    if member.guild_permissions.administrator:
        await ctx.respond(tr(uid, gid, "err_admin_t"), ephemeral=True); return
    sec = парсить_время(time_str)
    if not sec or sec < 10:
        await ctx.respond(tr(uid, gid, "err_bad_time"), ephemeral=True); return
    if sec > 28 * 86400:
        await ctx.respond(tr(uid, gid, "err_max_28d"), ephemeral=True); return
    try:
        await member.timeout_for(timedelta(seconds=sec),
                                 reason=f"{ctx.author}: {reason}")
    except Exception as e:
        await ctx.respond(f"❌ {e}", ephemeral=True); return
    добавить_наказание(gid, member.id, "mute", reason, uid, duration=sec)
    try:
        await member.send(tr(member.id, gid, "mute_dm",
                             dur=человеческое_время(sec), guild=ctx.guild.name,
                             reason=reason))
    except Exception:
        pass
    await ctx.respond(tr(uid, gid, "mute_done", user=member.mention,
                         dur=человеческое_время(sec), reason=reason))
    await лог_админа(ctx.guild, ctx.author, "Silenzio",
                     f"{member.mention} → {человеческое_время(sec)}\nReason: {reason}")


@bot.slash_command(name="unmute", description="Remove mute / Снять мут",
                   default_member_permissions=_мп())
async def cmd_unmute(ctx: discord.ApplicationContext, member: discord.Member):
    if await _сим_блок(ctx): return
    uid = ctx.author.id; gid = ctx.guild.id
    try:
        await member.remove_timeout(reason=f"Unmuted by {ctx.author}")
    except Exception as e:
        await ctx.respond(f"❌ {e}", ephemeral=True); return
    await ctx.respond(tr(uid, gid, "unmute_done", user=member.mention))
    await лог_админа(ctx.guild, ctx.author, "Unmute", f"{member.mention}")


@bot.slash_command(name="kick", description="Kick / Изгнать",
                   default_member_permissions=_мп())
async def cmd_kick(
    ctx: discord.ApplicationContext,
    member: discord.Member,
    reason: discord.Option(str, "Reason / Причина", required=True),
):
    if await _сим_блок(ctx): return
    uid = ctx.author.id; gid = ctx.guild.id
    if member.bot or member.id == uid:
        await ctx.respond("❌", ephemeral=True); return
    if member.guild_permissions.administrator:
        await ctx.respond(tr(uid, gid, "err_admin_t"), ephemeral=True); return
    if member.top_role >= ctx.author.top_role:
        await ctx.respond(tr(uid, gid, "err_higher_role"), ephemeral=True); return
    добавить_наказание(gid, member.id, "kick", reason, uid)
    try:
        await member.send(tr(member.id, gid, "kick_dm",
                             guild=ctx.guild.name, reason=reason))
    except Exception:
        pass
    try:
        await member.kick(reason=f"{ctx.author}: {reason}")
    except Exception as e:
        await ctx.respond(f"❌ {e}", ephemeral=True); return
    await ctx.respond(tr(uid, gid, "kick_done", user=member.mention, reason=reason))
    await лог_админа(ctx.guild, ctx.author, "Kick",
                     f"{member.mention} (`{member.id}`)\nReason: {reason}")


@bot.slash_command(name="ban", description="Ban forever / Забанить",
                   default_member_permissions=discord.Permissions(ban_members=True))
async def cmd_ban(
    ctx: discord.ApplicationContext,
    member: discord.Member,
    reason: discord.Option(str, "Reason / Причина", required=True),
    delete_days: discord.Option(int, "Delete msgs (0-7)", min_value=0,
                                max_value=7, default=0),
):
    if await _сим_блок(ctx): return
    uid = ctx.author.id; gid = ctx.guild.id
    if member.bot or member.id == uid:
        await ctx.respond("❌", ephemeral=True); return
    if member.guild_permissions.administrator:
        await ctx.respond(tr(uid, gid, "err_admin_t"), ephemeral=True); return
    if member.top_role >= ctx.author.top_role:
        await ctx.respond(tr(uid, gid, "err_higher_role"), ephemeral=True); return
    добавить_наказание(gid, member.id, "ban", reason, uid, delete_days=delete_days)
    try:
        await member.send(tr(member.id, gid, "ban_dm",
                             guild=ctx.guild.name, reason=reason))
    except Exception:
        pass
    try:
        await member.ban(reason=f"{ctx.author}: {reason}",
                         delete_message_seconds=delete_days * 86400)
    except Exception as e:
        await ctx.respond(f"❌ {e}", ephemeral=True); return
    await ctx.respond(tr(uid, gid, "ban_done", user=member.mention,
                         reason=reason, uid=member.id))
    await лог_админа(ctx.guild, ctx.author, "Ban",
                     f"{member.mention} (`{member.id}`)\nReason: {reason}")


@bot.slash_command(name="unban", description="Unban by ID",
                   default_member_permissions=discord.Permissions(ban_members=True))
async def cmd_unban(
    ctx: discord.ApplicationContext,
    user_id: discord.Option(str, "User ID", required=True),
    reason: discord.Option(str, "Reason", required=False, default="—"),
):
    if await _сим_блок(ctx): return
    uid = ctx.author.id; gid = ctx.guild.id
    if not user_id.isdigit():
        await ctx.respond(tr(uid, gid, "err_bad_id"), ephemeral=True); return
    tid = int(user_id)
    try:
        user = await bot.fetch_user(tid)
    except discord.NotFound:
        await ctx.respond(tr(uid, gid, "err_user_no"), ephemeral=True); return
    try:
        await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
    except discord.NotFound:
        await ctx.respond(tr(uid, gid, "err_not_banned"), ephemeral=True); return
    except Exception as e:
        await ctx.respond(f"❌ {e}", ephemeral=True); return
    добавить_наказание(gid, tid, "unban", reason, uid)
    await ctx.respond(tr(uid, gid, "unban_done", user=user.name, reason=reason))
    await лог_админа(ctx.guild, ctx.author, "Unban",
                     f"{user.mention} (`{tid}`)\nReason: {reason}")


@bot.slash_command(name="history", description="Punishment history / Досье",
                   default_member_permissions=_мп())
async def cmd_history(ctx: discord.ApplicationContext, member: discord.Member):
    uid = ctx.author.id; gid = ctx.guild.id
    recs = _наказания.get(gid, {}).get(member.id, [])
    if not recs:
        await ctx.respond(tr(uid, gid, "hist_empty", user=member.mention),
                          ephemeral=True)
        return
    embed = discord.Embed(
        title=tr(uid, gid, "hist_title", name=member.display_name),
        color=discord.Color.dark_red(),
        timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=member.display_avatar.url)
    icons = {"warn": "⚠️", "mute": "🔇", "kick": "👢", "ban": "🔨", "unban": "✅"}
    lines = []
    for rec in recs[-15:]:
        t = rec.get("type", "?")
        icon = icons.get(t, "❓")
        ts = datetime.fromtimestamp(rec.get("ts", 0), timezone.utc).strftime("%d.%m.%Y %H:%M")
        mod = ctx.guild.get_member(rec.get("mod_id", 0))
        if mod:
            mod_name = mod.display_name
        elif rec.get("mod_id") == (bot.user.id if bot.user else -1):
            mod_name = tr(uid, gid, "hist_auto")
        else:
            mod_name = f"ID:{rec.get('mod_id', '?')}"
        extra = f" [{человеческое_время(rec['duration'])}]" if rec.get("duration") else ""
        exp = f" *{tr(uid, gid, 'hist_expired')}*" if rec.get("expired") else ""
        lines.append(
            f"{icon} **{t.upper()}**{extra}{exp}\n"
            f"   {tr(uid, gid, 'hist_reason')}: {rec.get('reason', '—')}\n"
            f"   {tr(uid, gid, 'hist_mod')}: {mod_name}")
    embed.description = "\n\n".join(lines)
    embed.set_footer(text=tr(uid, gid, "hist_total", n=len(recs)))
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="serverinfo", description="Server info / Инфо о сервере",
                   default_member_permissions=discord.Permissions(administrator=True))
async def cmd_serverinfo(ctx: discord.ApplicationContext):
    g = ctx.guild
    humans = sum(1 for m in g.members if not m.bot)
    bots_n = g.member_count - humans
    embed = discord.Embed(title=f"📊 {g.name}",
                          color=discord.Color.dark_gold(),
                          timestamp=datetime.now(timezone.utc))
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👑 Owner", value=g.owner.mention, inline=True)
    embed.add_field(name="📅 Created", value=g.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="🆔 ID", value=f"`{g.id}`", inline=True)
    embed.add_field(name="👥 Members", value=f"**{humans}** + **{bots_n}** bots", inline=True)
    embed.add_field(name="📁 Channels", value=f"**{len(g.text_channels)}** / **{len(g.voice_channels)}**", inline=True)
    embed.add_field(name="🎭 Roles", value=f"**{len(g.roles)}**", inline=True)
    embed.add_field(name="🚀 Boost", value=f"Tier **{g.premium_tier}** • **{g.premium_subscription_count}**", inline=True)
    await ctx.respond(embed=embed, ephemeral=True)


class МодалкаДобавитьСлово(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title="➕ Add word / Добавить слово")
        self.add_item(InputText(label="Word / Слово", placeholder="word",
                                style=discord.InputTextStyle.short,
                                required=True, max_length=50))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        w = self.children[0].value.strip().lower()
        if not w:
            await interaction.response.send_message("❌", ephemeral=True); return
        s = получить_настройки(gid)
        if w in s["bad_words"]:
            await interaction.response.send_message("❌", ephemeral=True); return
        s["bad_words"].append(w)
        сохранить_настройки()
        await interaction.response.send_message(f"✅ `{w}`", ephemeral=True)
        await лог_админа(interaction.guild, interaction.user, "Filter +", f"`{w}`")


class МодалкаУбратьСлово(Modal):
    def __init__(self, uid: int, gid: int):
        super().__init__(title="➖ Remove word / Убрать слово")
        self.add_item(InputText(label="Word / Слово", placeholder="word",
                                style=discord.InputTextStyle.short,
                                required=True, max_length=50))

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id; gid = interaction.guild.id
        w = self.children[0].value.strip().lower()
        s = получить_настройки(gid)
        if w not in s["bad_words"]:
            await interaction.response.send_message("❌", ephemeral=True); return
        s["bad_words"].remove(w)
        сохранить_настройки()
        await interaction.response.send_message(f"✅ `{w}`", ephemeral=True)
        await лог_админа(interaction.guild, interaction.user, "Filter -", f"`{w}`")


class ПанельАвтомода(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.add_item(КнопкаЗакрыть(0, guild.id, row=3))

    @discord.ui.button(label="➕ Add", style=discord.ButtonStyle.success, row=0)
    async def add(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаДобавитьСлово(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="➖ Remove", style=discord.ButtonStyle.danger, row=0)
    async def rem(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(
            МодалкаУбратьСлово(interaction.user.id, interaction.guild.id))

    @discord.ui.button(label="📜 List", style=discord.ButtonStyle.secondary, row=1)
    async def lst(self, button: Button, interaction: discord.Interaction):
        s = получить_настройки(interaction.guild.id)
        words = s.get("bad_words", [])
        text = ", ".join(f"`{w}`" for w in words) if words else "*empty*"
        if len(text) > 1900: text = text[:1900] + "..."
        await interaction.response.send_message(f"📜 `{len(words)}`:\n\n{text}",
                                                ephemeral=True)

    @discord.ui.button(label="🔄 On/Off", style=discord.ButtonStyle.primary, row=1)
    async def tog(self, button: Button, interaction: discord.Interaction):
        s = получить_настройки(interaction.guild.id)
        s["automod_enabled"] = not s.get("automod_enabled", True)
        сохранить_настройки()
        st = "on" if s["automod_enabled"] else "off"
        await interaction.response.send_message(f"✅ {st}", ephemeral=True)


@bot.slash_command(name="automod", description="Filter / Фильтр",
                   default_member_permissions=discord.Permissions(administrator=True))
async def cmd_automod(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    s = получить_настройки(gid)
    st = "✅ on" if s.get("automod_enabled", True) else "❌ off"
    embed = discord.Embed(
        title="🛡️ Filter",
        description=(f"State: {st}\nWords: `{len(s.get('bad_words', []))}`\n"
                     f"Anti-spam: {ПОРОГ_СПАМА}+ / {ОКНО_СПАМА}s"),
        color=discord.Color.dark_gold())
    await ctx.respond(embed=embed, view=ПанельАвтомода(ctx.guild), ephemeral=True)


# ============================================================
# БЛЭКДЖЕК (КОМАНДА ЗАПУСКА)
# ============================================================
@bot.slash_command(name="bj", description="Blackjack vs bot / Блэкджек против бота")
async def cmd_bj(ctx: discord.ApplicationContext,
                 bet: discord.Option(int, "Ставка (50–10000)", min_value=50,
                                     max_value=10000, default=100) = 100):
    uid = ctx.author.id; gid = ctx.guild.id
    if (gid, uid) in _бдж_активные:
        entry = _бдж_активные.get((gid, uid), {})
        if time.time() - entry.get("ts", 0) > 600:
            _бдж_активные.pop((gid, uid), None)
        else:
            await ctx.respond(tr(uid, gid, "bj_active"), ephemeral=True)
            return
    st = получить_статы(gid, uid)
    if st["coins"] < bet:
        await ctx.respond(tr(uid, gid, "bj_need_coins").format(bet, st["coins"]), ephemeral=True); return
    st["coins"] -= bet; сохранить_данные()
    _бдж_активные[(gid, uid)] = {"type": "bj", "ts": time.time()}

    deck = _бдж_колода()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    
    # ФИКС: класс называется БДЖПротивБота, а не БДЖПротивБотаView
    view = БДЖПротивБота(uid, gid, bet, player, dealer, deck)

    if _бдж_блэкджек(player):
        while _бдж_значение(dealer) < 17: dealer.append(deck.pop())
        dv = _бдж_значение(dealer)
        if _бдж_блэкджек(dealer):
            st["coins"] += bet; log = tr(uid, gid, "bj_both_bj")
        else:
            win = int(bet * 1.5); st["coins"] += bet + win
            log = tr(uid, gid, "bj_bj_deal").format(win)
        сохранить_данные()
        _бдж_активные.pop((gid, uid), None)
        e = discord.Embed(title=tr(uid, gid, "bj_result_title"),
                          color=discord.Color.dark_green())
        e.add_field(name=tr(uid, gid, "bj_you"), value=f"{_бдж_рука(player)} → **21**", inline=False)
        e.add_field(name=tr(uid, gid, "bj_dealer"), value=f"{_бдж_рука(dealer)} → **{dv}**", inline=False)
        e.add_field(name="📝", value=log, inline=False)
        await ctx.respond(embed=e, ephemeral=True); return

    await ctx.respond(embed=view._эмбед(tr(uid, gid, "bj_deal")),
                      view=view, ephemeral=True)


@bot.slash_command(name="poker", description="Texas Hold'em multiplayer / Покер")
async def cmd_poker(
    ctx: discord.ApplicationContext,
    buyin: discord.Option(int, "Бай-ин (100–5000)", min_value=100,
                          max_value=5000, default=500) = 500,
    min_players: discord.Option(int, "Мин. игроков (2–6)", min_value=2,
                                max_value=6, default=2) = 2,
    max_players: discord.Option(int, "Макс. игроков (2–6)", min_value=2,
                                max_value=6, default=6) = 6,
    turn_time: discord.Option(int, "Секунд на ход (15–180)", min_value=15,
                              max_value=180, default=60) = 60,
):
    uid = ctx.author.id; gid = ctx.guild.id
    if min_players > max_players:
        await ctx.respond(f"❌ min ({min_players}) > max ({max_players}).",
                          ephemeral=True); return

    if not isinstance(ctx.channel, discord.TextChannel):
        await ctx.respond("❌ Только в обычном текстовом канале.", ephemeral=True); return

    st = получить_статы(gid, uid)
    if st["coins"] < buyin:
        await ctx.respond(f"❌ Нужно **{buyin}** 💰, у вас **{st['coins']}** 💰.",
                          ephemeral=True); return

    stamp = int(time.time()) % 100000
    thread_name = f"🃏 Poker #{stamp} — {ctx.author.display_name}"

    try:
        thread = await ctx.channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.public_thread,
            auto_archive_duration=1440)
        log.info(f"Создана ветка покера: {thread.name} (id={thread.id})")
    except discord.Forbidden:
        await ctx.respond("❌ Не могу создать ветку. Дай боту **Manage Threads**.",
                          ephemeral=True); return
    except discord.HTTPException as e:
        await ctx.respond(f"❌ Ошибка Discord: `{type(e).__name__}: {e}`", ephemeral=True); return
    except Exception as e:
        await ctx.respond(f"❌ Unexpected: `{type(e).__name__}: {e}`", ephemeral=True); return

    lobby = ПКЛобби(uid, gid, buyin, min_players, max_players, turn_time)
    lobby.thread_id = thread.id
    await thread.send(embed=lobby._эмбед(), view=lobby)
    await ctx.respond(f"🎰 Стол создан в {thread.mention}\nХост — {ctx.author.mention}.",
                      ephemeral=True)


# ============================================================
# НОВЫЕ ИГРЫ (ASK, STORY)
# ============================================================
@bot.slash_command(name="ask", description="Ask the Don a question / Спросить Дона")
async def cmd_ask(ctx: discord.ApplicationContext, question: discord.Option(str, "Your question / Ваш вопрос", required=True)):
    uid = ctx.author.id; gid = ctx.guild.id
    lang = получить_статы(gid, uid).get("lang", "en")
    
    r = random.random()
    if r < 0.45:
        ans = tr(uid, gid, "ask_yes")
        extra = random.choice(["Fatto!", "Il Don vede tutto.", "Sì, certo.", "Senza dubbio."])
        color = discord.Color.green()
    elif r < 0.75:
        ans = tr(uid, gid, "ask_no")
        extra = random.choice(["Codardo!", "Non ora.", "No.", "Assolutamente no."])
        color = discord.Color.red()
    else:
        ans = tr(uid, gid, "ask_maybe")
        extra = random.choice(["Il Don vede tutto...", "Chi lo sa.", "Aspetta.", "Forse."])
        color = discord.Color.gold()

    embed = discord.Embed(title=tr(uid, gid, "ask_title"), color=color)
    embed.add_field(name=tr(uid, gid, "ask_question"), value=question, inline=False)
    embed.add_field(name="🎩", value=f"{ans}\n*{extra}*", inline=False)
    embed.set_footer(text=f"👤 {ctx.author.display_name}")
    
    await ctx.respond(embed=embed)


@bot.slash_command(name="story", description="Family interactive story / Интерактивная история")
async def cmd_story(ctx: discord.ApplicationContext):
    uid = ctx.author.id; gid = ctx.guild.id
    view = StoryView(uid, gid, "start")
    await ctx.respond(tr(uid, gid, "story_start"), view=view)


# ============================================================
# ФОНОВЫЕ ЗАДАЧИ
# ============================================================
@tasks.loop(minutes=5)
async def проверить_истёкшие_муты():
    now = time.time()
    changed = False
    for g_id, users in list(_наказания.items()):
        guild = bot.get_guild(g_id)
        if not guild: continue
        for u_id, recs in list(users.items()):
            for rec in recs:
                if rec.get("type") != "mute": continue
                if rec.get("expired"): continue
                dur = rec.get("duration", 0); ts = rec.get("ts", 0)
                if not dur or not ts: continue
                if now - ts >= dur:
                    rec["expired"] = True; changed = True
                    m = guild.get_member(u_id)
                    mention = m.mention if m else f"`{u_id}`"
                    embed = discord.Embed(
                        title="🔊 Silenzio expired",
                        description=(f"**{mention}**\nDuration was: "
                                     f"{человеческое_время(dur)}\nReason: "
                                     f"{rec.get('reason', '—')}"),
                        color=discord.Color.green())
                    await в_лог(guild, embed)
    if changed: сохранить_наказания()


@проверить_истёкшие_муты.before_loop
async def _b_em():
    await bot.wait_until_ready()


@tasks.loop(hours=1)
async def проверить_топ1():
    for guild in bot.guilds:
        if guild.id not in данные_юзеров: continue
        users = данные_юзеров[guild.id]
        if not users: continue
        top_id = max(users.items(), key=lambda x: x[1].get("xp", 0))[0]
        if top_id: await выдать_достижение(guild, top_id, "top1")


@проверить_топ1.before_loop
async def _b_top():
    await bot.wait_until_ready()


# ============================================================
# СОБЫТИЯ
# ============================================================
@bot.event
async def on_ready():
    log.info(f"{ИМЯ_БОТА} ({bot.user}) запущен!")
    for guild in bot.guilds:
        try:
            await bot.sync_commands(guild_ids=[guild.id], delete_existing=True)
            log.info(f"✅ Команды засинканы: {guild.name}")
        except Exception as e:
            log.error(f"❌ Ошибка синка на {guild.name}: {e}")
    for guild in bot.guilds:
        if guild.id in _инициализированные: continue
        _инициализированные.add(guild.id)
        log.info(f"🔧 Инициализация {guild.name}")
        await создать_роли(guild)

    if not проверить_истёкшие_муты.is_running():
        проверить_истёкшие_муты.start()
    if not проверить_топ1.is_running():
        проверить_топ1.start()
    if not чистка_зависших_покеров.is_running():
        чистка_зависших_покеров.start()

    await _восстановить_покер()


async def _восстановить_покер():
    """Пробует восстановить активные столы покера после рестарта."""
    saved = _покер_загрузить()
    if not saved:
        return
    log.info(f"Найдено {len(saved)} сохранённых столов покера")
    for mid, state in saved.items():
        try:
            ch = bot.get_channel(state["thread_id"])
            if not ch:
                log.warning(f"Ветка {state['thread_id']} не найдена — пропуск")
                continue
            try:
                await ch.fetch_message(state["public_msg_id"])
            except discord.NotFound:
                log.warning(f"Сообщение {mid} не найдено — пропуск")
                continue

            _покер_толы[mid] = state
            log.info(f"Восстановлен стол {mid}")

            if not state.get("finished"):
                cur_idx = state["current_idx"]
                cur_uid = state["players"][cur_idx]
                try:
                    await ch.send(f"🔄 <@{cur_uid}>, ваш ход. "
                                  f"Бот перезапущен, таймер пошёл заново.")
                except Exception:
                    pass
                _покер_таймеры[mid] = asyncio.create_task(
                    _пк_таймер(state, cur_uid))
                await _пк_эфе_ход(state, cur_uid)
        except Exception as e:
            log.error(f"Не смог восстановить стол {mid}: {e}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    _инициализированные.add(guild.id)
    await создать_роли(guild)
    try:
        await bot.sync_commands(guild_ids=[guild.id], delete_existing=True)
    except Exception as e:
        log.error(f"❌ Ошибка синка: {e}")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    log.exception(f"Ошибка в {ctx.command}: {error}")
    try:
        if ctx.response.is_done():
            await ctx.followup.send("❌ Errore. Try later.", ephemeral=True)
        else:
            await ctx.respond("❌ Errore. Try later.", ephemeral=True)
    except Exception:
        pass


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild: return

    try:
        if await защита_лог_канала(message): return
    except Exception as e:
        log.error(f"Ошибка защиты лога: {e}")
    try:
        if await проверить_автомод(message): return
    except Exception as e:
        log.error(f"Ошибка автомода: {e}")

    gid = message.guild.id; uid = message.author.id
    st = получить_статы(gid, uid)
    now = time.time()

    сбросить_миссии(st)

    if now - st.get("last_msg_mission_time", 0) >= КД_МИССИЯ_СООБЩ:
        st["missions"]["msg_count"] += 1
        st["last_msg_mission_time"] = now

    text_lower = "".join(message.content.lower().split())
    raw = message.content.lower()
    is_furry = "фурри" in text_lower or "фурри" in raw
    is_other = any(w in text_lower or w in raw
                   for w in ["пенис", "писка", "девочкакошка", "девочка кошка"])

    if is_furry:
        st["missions"]["furry_triggered"] = 1

        async def _sandwich():
            try:
                base = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(base, "sandwich.mp4")
                txt = ("Эй ты когда нибудь пробовал сэндвич со сгущенкой? "
                       "Нет сейчас узнаешь вот прям сейчас")
                if os.path.exists(path):
                    await message.channel.send(
                        txt, file=discord.File(path, filename="sandwich.mp4"))
                else:
                    await message.channel.send(f"{txt}\n*(⚠️ sandwich.mp4 missing!)*")
            except Exception as e:
                log.error(f"Ошибка фурри: {e}")
        asyncio.create_task(_sandwich())
    elif is_other:
        async def _w():
            try:
                await message.channel.send(f"⚠️ {message.author.mention}")
            except Exception:
                pass
        asyncio.create_task(_w())

    if now - st["last_xp_time"] >= КД_XP:
        has_video = any(a.content_type and "video" in a.content_type
                        for a in message.attachments)
        has_gif = (any(a.filename.endswith(".gif") for a in message.attachments)
                   or "tenor.com" in message.content
                   or "giphy.com" in message.content)
        if has_video:
            xp = 4; st["missions"]["media_count"] += 1
        elif has_gif:
            xp = 2; st["missions"]["media_count"] += 1
        else:
            xp = 2
        st["xp"] += xp
        st["coins"] += 5
        st["last_xp_time"] = now
        сохранить_данные()
        if isinstance(message.author, discord.Member):
            asyncio.create_task(проверить_роли(
                message.author, st["xp"], st["rank_override"]))
        if st["coins"] >= 100000:
            asyncio.create_task(выдать_достижение(message.guild, uid, "rich"))

    s = настройки_серверов.get(gid)
    if s and s.get("target") and s.get("emojis"):
        target = s["target"]; emojis = s["emojis"]
        if target.lower() in ("all", "все") or str(uid) == target:
            async def _r():
                for e in emojis:
                    try:
                        await message.add_reaction(e)
                    except Exception as ex:
                        log.warning(f"Реакция {e}: {ex}")
            asyncio.create_task(_r())

    await bot.process_commands(message)


# ============================================================
# ЧИСТКА ЗАВИСШИХ ПОКЕРОВ
# ============================================================
@tasks.loop(minutes=10)
async def чистка_зависших_покеров():
    """Удаляет ветки покера, которые висят без дела больше 30 минут."""
    now = time.time()
    удалено = 0
    активные_ветки = {s["thread_id"] for s in _покер_толы.values()}

    for mid, s in list(_покер_толы.items()):
        started = s.get("started_at", 0)
        if started and now - started > 1800:
            try:
                # удалить лобби-сообщение
                pid = s.get("parent_msg_id")
                pcid = s.get("parent_channel_id")
                if pid and pcid:
                    try:
                        pch = bot.get_channel(pcid)
                        if pch:
                            pmsg = await pch.fetch_message(pid)
                            await pmsg.delete()
                    except Exception:
                        pass
                # удалить ветку
                ch = bot.get_channel(s["thread_id"])
                if ch:
                    await ch.send("⏰ **Партия зависла — ветка удаляется.**")
                    await ch.delete()
                    удалено += 1
            except Exception:
                pass
            _покер_толы.pop(mid, None)
            _покер_сохранить()

    for guild in bot.guilds:
        for ch in guild.text_channels:
            try:
                threads = ch.threads
            except Exception:
                continue
            for th in threads:
                if not th.name.startswith("🃏 Poker #"):
                    continue
                if th.id in активные_ветки:
                    continue
                try:
                    age = (datetime.now(timezone.utc) - th.created_at).total_seconds()
                    if age > 1800:
                        await th.delete()
                        удалено += 1
                except Exception:
                    pass

    if удалено:
        log.info(f"🧹 Очищено зависших веток покера: {удалено}")


@чистка_зависших_покеров.before_loop
async def _b_clean():
    await bot.wait_until_ready()


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    if not TOKEN:
        log.critical("DISCORD_TOKEN не задан. Проверьте .env")
        raise SystemExit(1)
    bot.run(TOKEN)