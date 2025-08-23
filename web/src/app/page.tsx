"use client"
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import timeGridPlugin from '@fullcalendar/timegrid'
import { Fragment, useState, useCallback } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { ExclamationTriangleIcon } from '@heroicons/react/20/solid'
import type { EventSourceInput, DatesSetArg } from '@fullcalendar/core'
import { useRef } from "react"
import { CalendarApi } from '@fullcalendar/core'


interface Event {
  title: string;
  start: Date | string;
  allDay: boolean;
  id: number;
}

type Task = {
  task_id: number;
  title: string;
  start_time: string;        // ISO文字列
  required_time?: number;
  user_id?: number;
  is_task?: boolean | number;
  done?: boolean;
};

export default function Home() {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const [allEvents, setAllEvents] = useState<Event[]>([])
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [idToDelete, setIdToDelete] = useState<number | null>(null)
  const [newEvent, setNewEvent] = useState({
    title: '',
    start_time: '',       // ← start → start_time に
    required_time: 0,     // ← 所要時間を分で
    user_id: 1,           // ← とりあえず固定値でOK
    is_task: true         // ← タスクか予定かの判定
  });
  const calendarRef = useRef<any>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isAddModalOpen_schedule, setIsAddModalOpen_schedule] = useState(false)
  const [isAddModalOpen_task, setIsAddModalOpen_task] = useState(false)
  const [isTaskManageModalOpen, setIsTaskManageModalOpen] = useState(false)
  const [tasks, setTasks] = useState<{ id: number; title: string; date: string; time: string; hours: number }[]>([])
  const [durationHour, setDurationHour] = useState(0);
  const [durationMin, setDurationMin] = useState(0);

  const clamp = (n: number, min: number, max: number) => Math.min(max, Math.max(min, n));
  const updateRequiredMinutes = (h: number, m: number) => {
    const total = Math.max(0, h * 60 + m);
    setNewEvent(prev => ({ ...prev, required_time: total }));
  };
  const toJstIso = (dateStr: string, timeStr: string) => `${dateStr}T${timeStr}:00+09:00`;

  function handleDateClick(arg: { date: Date; allDay: boolean }) {
    const api = calendarRef.current?.getApi();
    if (!api) return;
    api.changeView('timeGridDay', arg.date);   // ← ここがポイント
  }

  function handleDeleteModal(data: { event: { id: string } }) {
    setShowDeleteModal(true)
    setIdToDelete(Number(data.event.id))
  }

  function handleDelete() {
    setAllEvents(allEvents.filter(event => Number(event.id) !== Number(idToDelete)))
    setShowDeleteModal(false)
    setIdToDelete(null)
  }

  // ---- “年・月”で1か月分を取得（URLは /tasks/month?year=&month= と仮定）----
  async function fetchMonthTasks(apiBase: string, year: number, month: number): Promise<Task[]> {
  const url = `${apiBase}/tasks/month?year=${year}&month=${month}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
  return res.json();
  }

// ---- FullCalendar イベントへマッピング ----
  function toEvents(tasks: Task[]) {
    return tasks.map(t => ({
      id: t.task_id,
      title: t.title ?? "(no title)",
      start: t.start_time,     // ISO そのまま
      allDay: false,
    }));
  }

  // FullCalendarの表示範囲が変わる度（初回含む）に発火
  const handleDatesSet = useCallback(async (info: any) => {
    const d: Date = info.start;            // 表示中ビューの先頭近辺
    const year = d.getFullYear();
    const month = d.getMonth() + 1;        // 1始まり

    try {
      const tasks = await fetchMonthTasks(API_BASE, year, month);
      setAllEvents(toEvents(tasks));
    } catch (e) {
      console.error("月間タスク取得に失敗:", e);
      setAllEvents([]);
    }
  }, [API_BASE]);

  const handleAddTask = async () => {

  if (!newEvent.title || !newEvent.start_time || !newEvent.required_time) {
    alert("すべての項目を入力してください");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newEvent, is_task: true, user_id: 1 }),
    });

    if (res.ok) {
      const data = await res.json();
      console.log("保存成功:", data);

    // 今ある setAllEvents([...allEvents, {...}]) は削除してOK
    const api = calendarRef.current?.getApi();
    if (api) {
      const cs: Date = api.view.currentStart;
      const y = cs.getFullYear(), m = cs.getMonth() + 1;
      const tasks = await fetchMonthTasks(API_BASE, y, m);
      setAllEvents(toEvents(tasks));
    }

      setIsAddModalOpen_task(false); // モーダルを閉じる
      setNewEvent({ title: '', start_time: '', required_time: 0, user_id: 1, is_task: true });
    } else {
      console.error("保存失敗", await res.text());
    }
  } catch (err) {
    console.error("通信エラー", err);
  }
};

const handleAddSchedule = async () => {

  if (!newEvent.title || !newEvent.start_time || !newEvent.required_time) {
    alert("すべての項目を入力してください");
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newEvent, is_task: false }),
    });

    if (res.ok) {
      const data = await res.json();
      console.log("予定保存成功:", data);

     const api = calendarRef.current?.getApi();
      if (api) {
       const cs: Date = api.view.currentStart;
       const y = cs.getFullYear(), m = cs.getMonth() + 1;
       const tasks = await fetchMonthTasks(API_BASE, y, m);
       setAllEvents(toEvents(tasks));
      }

      setIsAddModalOpen_schedule(false);
      setNewEvent({ title: '', start_time: '', required_time: 0, user_id: 1, is_task: true });
    } else {
      console.error("予定保存失敗", await res.text());
    }
  } catch (err) {
    console.error("通信エラー", err);
  }
};

const closeDeleteModal = () => {
  setShowDeleteModal(false);
  setIdToDelete(null);
};


  return (
    <>
      <nav className="flex justify-between mb-12 border-b border-violet-100 p-4">
        <h1 className="font-bold text-2xl text-gray-700">俺らのカレンダー</h1>
      </nav>
      <main className="flex min-h-screen flex-col items-center justify-between p-24">
        <div className="w-full">
          <FullCalendar
            ref={calendarRef}
            plugins={[dayGridPlugin, interactionPlugin, timeGridPlugin]}
            headerToolbar={{
              left: 'today prev',
              center: 'title',
              right: 'next dayGridMonth,timeGridWeek hamburger'
            }}
            customButtons={{
                hamburger: {
                text: '☰', // ← ハンバーガーアイコン
                click: () => setIsSidebarOpen(true)
              }
            }}
            initialView="dayGridMonth"
            datesSet={handleDatesSet}
            events={allEvents as EventSourceInput}
            nowIndicator={true}
            editable={true}
            selectable={false}
            selectMirror={true}
            dateClick={handleDateClick}
            eventClick={(data) => handleDeleteModal(data)}
          />
        </div>

                {/* サイドバー */}
        <div
          className={`fixed top-0 right-0 h-full w-64 bg-violet-50 shadow-lg transform 
          ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full'} 
          transition-transform duration-300 ease-in-out z-50`}
        >
          <div className="p-4 border-b flex justify-between items-center">
            <h2 className="text-9xl font-bold">メニュー</h2>
          <button 
            onClick={() => setIsSidebarOpen(false)} 
            className="text-xl font-bold text-gray-500 hover:text-gray-700 leading-none"
          >
            ✕
          </button>
          </div>
          <ul className="p-4 space-y-4 text-3xl">
            <li>
              <button 
                onClick={() => setIsTaskManageModalOpen(true)}
                className="w-full px-4 py-3 rounded-lg bg-violet-600 text-white font-semibold shadow-md hover:bg-violet-700 transition">
                タスク管理
              </button>
            </li>
            <li>
              <button 
                onClick={() => {
                  setDurationHour(0);
                  setDurationMin(0);
                  setNewEvent(e => ({ ...e, is_task: true }));   // タスク
                  setIsAddModalOpen_task(true);
                }}
                className="w-full px-4 py-3 rounded-lg bg-violet-600 text-white font-semibold shadow-md hover:bg-violet-700 transition">
                タスク追加
              </button>

              <button
                onClick={() => {
                  setDurationHour(0);
                  setDurationMin(0);
                  setNewEvent(e => ({ ...e, is_task: false }));  // 予定
                  setIsAddModalOpen_schedule(true);
                }}
                className="w-full px-4 py-3 rounded-lg bg-violet-600 text-white font-semibold shadow-md hover:bg-violet-700 transition"
              >
                予定追加
              </button>
            </li>
          </ul>
        </div>

        {isAddModalOpen_schedule && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
            <div className="bg-white rounded-lg shadow-lg w-96 p-6">
              <h2 className="text-2xl font-bold mb-4">予定を追加</h2>

                  <input
                    type="text"
                    placeholder="タイトル"
                    value={newEvent.title}
                    onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                  />

                  <input
                    type="date"
                    onChange={(e) => {
                      const date = e.target.value;
                      const time = newEvent.start_time.split("T")[1]?.slice(0,5) || "00:00";
                      setNewEvent({ ...newEvent, start_time: toJstIso(date, time) });
                    }}
                  />

                  <input
                    type="time"
                    onChange={(e) => {
                      const time = e.target.value;
                      const date = newEvent.start_time.split("T")[0] || new Date().toISOString().slice(0,10);
                      setNewEvent({ ...newEvent, start_time: toJstIso(date, time) });
                    }}
                  />

                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min={0}
                      step={1}
                      className="w-20 border px-3 py-2 rounded"
                      value={durationHour}
                      onChange={(e) => {
                        const h = clamp(Number(e.target.value || 0), 0, 9999);
                        setDurationHour(h);
                        updateRequiredMinutes(h, durationMin);
                      }}
                      placeholder="時間"
                    />
                    <span>時間</span>

                    <input
                      type="number"
                      min={0}
                      max={59}
                      step={1}
                      className="w-20 border px-3 py-2 rounded"
                      value={durationMin}
                      onChange={(e) => {
                        const m = clamp(Number(e.target.value || 0), 0, 59);
                        setDurationMin(m);
                        updateRequiredMinutes(durationHour, m);
                      }}
                      placeholder="分"
                    />
                    <span>分</span>
                  </div>

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setIsAddModalOpen_schedule(false)}
                  className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
                >
                  キャンセル
                </button>
                <button
                  onClick={handleAddSchedule}
                  className="px-4 py-2 rounded bg-violet-600 text-white hover:bg-violet-700"
                >
                  追加
                </button>
              </div>
            </div>
          </div>
        )}

        {isAddModalOpen_task && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
            <div className="bg-white rounded-lg shadow-lg w-96 p-6">
              <h2 className="text-2xl font-bold mb-4">タスクを追加</h2>

                <input
                  type="text"
                  placeholder="タイトル"
                  value={newEvent.title}
                  onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                />
                <input
                  type="date"
                  onChange={(e) => {
                    const date = e.target.value;
                    const time = newEvent.start_time.split("T")[1]?.slice(0,5) || "00:00";
                    setNewEvent({ ...newEvent, start_time: toJstIso(date, time) });
                  }}
                />
                <input
                  type="time"
                  onChange={(e) => {
                    const time = e.target.value;
                      const date = newEvent.start_time.split("T")[0] || new Date().toISOString().slice(0,10);
                      setNewEvent({ ...newEvent, start_time: toJstIso(date, time) });
                  }}
                />
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min={0}
                      step={1}
                      className="w-20 border px-3 py-2 rounded"
                      value={durationHour}
                      onChange={(e) => {
                        const h = clamp(Number(e.target.value || 0), 0, 9999);
                        setDurationHour(h);
                        updateRequiredMinutes(h, durationMin);
                      }}
                      placeholder="時間"
                    />
                    <span>時間</span>

                    <input
                      type="number"
                      min={0}
                      max={59}
                      step={1}
                      className="w-20 border px-3 py-2 rounded"
                      value={durationMin}
                      onChange={(e) => {
                        const m = clamp(Number(e.target.value || 0), 0, 59);
                        setDurationMin(m);
                        updateRequiredMinutes(durationHour, m);
                      }}
                      placeholder="分"
                    />
                    <span>分</span>
                  </div>

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setIsAddModalOpen_task(false)}
                  className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
                >
                  キャンセル
                </button>
                <button
                  onClick={handleAddTask}
                  className="px-4 py-2 rounded bg-violet-600 text-white hover:bg-violet-700"
                >
                  追加
                </button>
              </div>
            </div>
          </div>
        )}

        {isTaskManageModalOpen && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
            <div className="bg-white rounded-lg shadow-lg w-96 p-6">
              <h2 className="text-2xl font-bold mb-4">タスク管理</h2>

              {tasks.length === 0 ? (
                <p className="text-gray-500">まだタスクはありません</p>
              ) : (
                <ul className="space-y-2">
                  {tasks.map((task) => (
                    <li key={task.id} className="flex justify-between items-center border px-3 py-2 rounded">
                      <div>
                        <p className="font-semibold">{task.title}</p>
                        <p className="text-sm text-gray-500">{task.date} {task.time}（{task.hours}時間）</p>
                      </div>
                      <button 
                        onClick={() => setTasks(tasks.filter(t => t.id !== task.id))}
                        className="text-red-500 hover:text-red-700"
                      >
                        ✕
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              <div className="flex justify-end mt-4">
                <button
                  onClick={() => setIsTaskManageModalOpen(false)}
                  className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
                >
                  閉じる
                </button>
              </div>
            </div>
          </div>
        )}



        {/* 削除モーダル */}
        <Transition.Root show={showDeleteModal} as={Fragment}>
          <Dialog as="div" className="relative z-10" onClose={setShowDeleteModal}>
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
            </Transition.Child>

            <div className="fixed inset-0 z-10 overflow-y-auto">
              <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                <Transition.Child
                  as={Fragment}
                  enter="ease-out duration-300"
                  enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                  enterTo="opacity-100 translate-y-0 sm:scale-100"
                  leave="ease-in duration-200"
                  leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                  leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                >
                  <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
                    <div className="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                      <div className="sm:flex sm:items-start">
                        <div className="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                          <ExclamationTriangleIcon className="h-6 w-6 text-red-600" aria-hidden="true" />
                        </div>
                        <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                          <Dialog.Title as="h3" className="text-base font-semibold leading-6 text-gray-900">
                            Delete Event
                          </Dialog.Title>
                          <div className="mt-2">
                            <p className="text-sm text-gray-500">
                              Are you sure you want to delete this event?
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                      <button
                        type="button"
                        className="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                        onClick={handleDelete}
                      >
                        Delete
                      </button>
                      <button
                        type="button"
                        className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                        onClick={closeDeleteModal}
                      >
                        Cancel
                      </button>
                    </div>
                  </Dialog.Panel>
                </Transition.Child>
              </div>
            </div>
          </Dialog>
        </Transition.Root>

      </main>
    </>
  )
}
