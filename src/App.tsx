/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Calendar, Clock, Bell, Users, Shield, Terminal, BookOpen, Download, CheckCircle, ExternalLink } from 'lucide-react';

export default function App() {
  const [selectedGroup, setSelectedGroup] = useState<'MMT-950/26i' | 'MMT-951/26i'>('MMT-950/26i');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-blue-500/20">
              T
            </div>
            <div>
              <h1 className="text-base font-semibold text-white tracking-tight">TSUE Dars Jadvali Telegram Boti</h1>
              <p className="text-xs text-slate-400">Toshkent Davlat Iqtisodiyot Universiteti</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Backend Bot Tayyor
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-950/50 via-slate-900 to-indigo-950/50 border border-slate-800/80 rounded-2xl p-6 sm:p-8 relative overflow-hidden">
          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Calendar className="w-3.5 h-3.5" />
              aSc Timetables uslubida Pillow render va aiogram 3 boti
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              TDIU Talabalari Uchun Dars Jadvali Boti
            </h2>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Bot to'liq Python 3.12 va aiogram 3 asosida yaratildi. MMT-950/26i va MMT-951/26i guruhlarining
              haqiqiy jadvallari, A/B hafta hisob-kitobi, 10 daqiqa oldin eslatmalar va guruh chatlariga tonggi jadval yuborish funksiyalari faol.
            </p>
          </div>
        </div>

        {/* Group Selector and Preview */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Generatsiya Qilingan Dars Jadvallari</h3>
              <p className="text-xs text-slate-400">Pillow kutubxonasi orqali chizilgan rasmiy aSc formati</p>
            </div>
            <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setSelectedGroup('MMT-950/26i')}
                className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                  selectedGroup === 'MMT-950/26i'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                MMT-950/26i
              </button>
              <button
                onClick={() => setSelectedGroup('MMT-951/26i')}
                className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                  selectedGroup === 'MMT-951/26i'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                MMT-951/26i
              </button>
            </div>
          </div>

          {/* Rendered Timetable View */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-semibold text-white">{selectedGroup} — Moliya va Bank ishi (1-kurs)</span>
              </div>
              <a
                href={selectedGroup === 'MMT-950/26i' ? '/samples/timetable_MMT_950_26i.png' : '/samples/timetable_MMT_951_26i.png'}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium"
              >
                <Download className="w-3.5 h-3.5" />
                Asl PNG ni yuklab olish
              </a>
            </div>

            <div className="rounded-xl overflow-hidden border border-slate-800 bg-white">
              <img
                src={selectedGroup === 'MMT-950/26i' ? '/samples/timetable_MMT_950_26i.png' : '/samples/timetable_MMT_951_26i.png'}
                alt={`Timetable ${selectedGroup}`}
                className="w-full h-auto object-contain"
              />
            </div>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl space-y-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white">A/B Hafta va Eslatmalar</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              2026-yil 7-sentabrdan boshlab juft/toq haftalar avtomatik hisoblanadi. Har bir darsdan 10 daqiqa oldin xabar jo'natiladi.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl space-y-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white">Guruh Chatlari Qo'llab-quvvatlanishi</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Bot Telegram guruh chatlariga qo'shilib, <code>/setgroup MMT-950/26i</code> buyrug'i orqali har tong 07:00 da dars jadvalini guruhga avtomatik jo'natadi.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl space-y-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <Shield className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white">Telegram Ichidagi Admin Panel</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Adminlar uchun <code>/admin</code>, <code>/stats</code>, 2-bosqichli tasdiq kodiga ega <code>/broadcast</code>, hamda avtomatik SQLite <code>/backup</code> xizmati mavjud.
            </p>
          </div>
        </div>

        {/* Commands Reference Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-400" />
            Telegram Buyruqlari Malumotnomasi
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Buyruq</th>
                  <th className="py-2.5 px-3">Qo'llanishi</th>
                  <th className="py-2.5 px-3">Tavsif</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                <tr>
                  <td className="py-2.5 px-3 font-mono text-blue-400">/start</td>
                  <td className="py-2.5 px-3">Shaxsiy chat</td>
                  <td className="py-2.5 px-3">Botni ishga tushirish, guruh tanlash menyusi</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-mono text-blue-400">/setgroup &lt;Nomi&gt;</td>
                  <td className="py-2.5 px-3">Guruh chati</td>
                  <td className="py-2.5 px-3">Chatni MMT-950/26i yoki MMT-951/26i ga biriktirish</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-mono text-blue-400">/settime &lt;HH:MM&gt;</td>
                  <td className="py-2.5 px-3">Guruh chati</td>
                  <td className="py-2.5 px-3">Ertalabki avtomatik jadval yuborish vaqtini belgilash</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-mono text-blue-400">/admin</td>
                  <td className="py-2.5 px-3">Admin shaxsiy chati</td>
                  <td className="py-2.5 px-3">Statistika, foydalanuvchilar, sinxronizatsiya, backup menyusi</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-mono text-blue-400">/backup</td>
                  <td className="py-2.5 px-3">Admin shaxsiy chati</td>
                  <td className="py-2.5 px-3">Baza zaxira nusxasini olib, .gz faylni telegramga yuklash</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>TSUE Dars Jadvali Boti &bull; Toshkent Davlat Iqtisodiyot Universiteti &bull; Python 3.12, aiogram 3 & Pillow</p>
      </footer>
    </div>
  );
}
