"use client"
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import timeGridPlugin from '@fullcalendar/timegrid'
import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { CheckIcon, ExclamationTriangleIcon } from '@heroicons/react/20/solid'
import { EventSourceInput } from '@fullcalendar/core/index.js'
import { useRef } from "react"
import { CalendarApi } from '@fullcalendar/core'


interface Event {
  title: string;
  start: Date | string;
  allDay: boolean;
  id: number;
}

export default function Home() {
  const [allEvents, setAllEvents] = useState<Event[]>([])
  const [showModal, setShowModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [idToDelete, setIdToDelete] = useState<number | null>(null)
  const [newEvent, setNewEvent] = useState<Event>({
    title: '',
    start: '',
    allDay: false,
    id: 0
  })
  const calendarRef = useRef<any>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isAddModalOpen_schedule, setIsAddModalOpen_schedule] = useState(false)
  const [isAddModalOpen_task, setIsAddModalOpen_task] = useState(false)
  const [isTaskManageModalOpen, setIsTaskManageModalOpen] = useState(false)
  const [tasks, setTasks] = useState<{ id: number; title: string; date: string; time: string; hours: number }[]>([])




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

  function handleCloseModal() {
    setShowModal(false)
    setNewEvent({
      title: '',
      start: '',
      allDay: false,
      id: 0
    })
    setShowDeleteModal(false)
    setIdToDelete(null)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setNewEvent({
      ...newEvent,
      title: e.target.value
    })
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setAllEvents([...allEvents, newEvent])
    setShowModal(false)
    setNewEvent({
      title: '',
      start: '',
      allDay: false,
      id: 0
    })
  }

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
                onClick={() => setIsAddModalOpen_task(true)}
                className="w-full px-4 py-3 rounded-lg bg-violet-600 text-white font-semibold shadow-md hover:bg-violet-700 transition">
                タスク追加
              </button>
            </li>
            <li>
            <button
              onClick={() => setIsAddModalOpen_schedule(true)}
              className="w-full px-4 py-3 rounded-lg bg-violet-600 text-white font-semibold shadow-md hover:bg-violet-700 transition"
            >
              予定追加
            </button>
            </li>
          </ul>
        </div>

        {isAddModalOpen_schedule && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-black/40 z-50">
            <div className="bg-white rounded-lg shadow-lg w-96 p-6">
              <h2 className="text-2xl font-bold mb-4">予定を追加</h2>

              <input
                type="text"
                placeholder="タイトル"
                className="w-full border px-3 py-2 rounded mb-3"
              />
              <input
                type="date"
                className="w-full border px-3 py-2 rounded mb-3"
              />
              <input
                type="time"
                className="w-full border px-3 py-2 rounded mb-3"
              />
              <input
                type="number"
                placeholder="時間"
                className="w-full border px-3 py-2 rounded mb-3"
              />

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setIsAddModalOpen_schedule(false)}
                  className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
                >
                  キャンセル
                </button>
                <button
                  onClick={() => {
                    // TODO: 予定追加処理
                    setIsAddModalOpen_schedule(false)
                  }}
                  className="px-4 py-2 rounded bg-violet-600 text-white hover:bg-violet-700"
                >
                  追加
                </button>
              </div>
            </div>
          </div>
        )}

        {isTaskManageModalOpen && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-black/40 z-50">
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

        {isAddModalOpen_task && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-black/40 z-50">
            <div className="bg-white rounded-lg shadow-lg w-96 p-6">
              <h2 className="text-2xl font-bold mb-4">タスクを追加</h2>

              <input
                type="text"
                placeholder="タイトル"
                className="w-full border px-3 py-2 rounded mb-3"
              />
              <input
                type="date"
                className="w-full border px-3 py-2 rounded mb-3"
              />
              <input
                type="time"
                className="w-full border px-3 py-2 rounded mb-3"
              />
              <input
                type="number"
                placeholder="時間"
                className="w-full border px-3 py-2 rounded mb-3"
              />

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setIsAddModalOpen_task(false)}
                  className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
                >
                  キャンセル
                </button>
                <button
                  onClick={() => {
                    // TODO: 予定追加処理
                    setIsAddModalOpen_task(false)
                  }}
                  className="px-4 py-2 rounded bg-violet-600 text-white hover:bg-violet-700"
                >
                  追加
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
                        onClick={handleCloseModal}
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
        
        {/* 追加モーダル */}
        <Transition.Root show={showModal} as={Fragment}>
          <Dialog as="div" className="relative z-10" onClose={setShowModal}>
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
                  <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                    <div>
                      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                        <CheckIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
                      </div>
                      <div className="mt-3 text-center sm:mt-5">
                        <Dialog.Title as="h3" className="text-base font-semibold leading-6 text-gray-900">
                          Add Event
                        </Dialog.Title>
                        <form action="submit" onSubmit={handleSubmit}>
                          <div className="mt-2">
                            <input
                              type="text"
                              name="title"
                              className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 
                              focus:ring-2 focus:ring-inset focus:ring-violet-600 sm:text-sm sm:leading-6"
                              value={newEvent.title}
                              onChange={(e) => handleChange(e)}
                              placeholder="Title"
                            />
                          </div>
                          <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                            <button
                              type="submit"
                              className="inline-flex w-full justify-center rounded-md bg-violet-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-600 sm:col-start-2 disabled:opacity-25"
                              disabled={newEvent.title === ''}
                            >
                              Create
                            </button>
                            <button
                              type="button"
                              className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                              onClick={handleCloseModal}
                            >
                              Cancel
                            </button>
                          </div>
                        </form>
                      </div>
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
