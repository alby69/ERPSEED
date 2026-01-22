import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { DndContext, closestCorners } from '@dnd-kit/core';
import { SortableContext, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useVirtualizer } from '@tanstack/react-virtual';
import { io } from 'socket.io-client';
import { Layout } from '../components';
import { useAuth } from '../context';
import { apiFetch, BASE_URL } from '../utils';

const TASK_STATUSES = ['todo', 'in_progress', 'review', 'done'];
const STATUS_LABELS = {
  todo: 'To Do',
  in_progress: 'In Corso',
  review: 'In Revisione',
  done: 'Completato'
};

function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [users, setUsers] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    status: 'todo',
    due_date: '',
    assigned_to_id: ''
  });

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const projectRes = await apiFetch(`/projects/${id}`);
        const projectData = await projectRes.json();
        setProject(projectData);

        // Fetch all tasks for the project, assuming pagination is not needed for the board
        const tasksRes = await apiFetch(`/project-tasks?project_id=${id}&per_page=1000`);
        const tasksData = await tasksRes.json();
        setTasks(tasksData);

        // Fetch users for assignment (best effort, might fail if not admin)
        try {
          const usersRes = await apiFetch('/users?per_page=100');
          if (usersRes.ok) {
            const usersData = await usersRes.json();
            setUsers(Array.isArray(usersData) ? usersData : (usersData.items || []));
          }
        } catch (e) {
          console.warn("Could not load users list");
        }

      } catch (error) {
        console.error("Failed to load project data", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [id]);

  // WebSocket Connection
  useEffect(() => {
    const socket = io(BASE_URL);

    socket.on('connect', () => {
      socket.emit('join', { room: `project_${id}` });
    });

    socket.on('task_created', (newTask) => {
      setTasks((prev) => [...prev, newTask]);
    });

    socket.on('task_updated', (updatedTask) => {
      setTasks((prev) => prev.map((t) => (t.id === updatedTask.id ? updatedTask : t)));
    });

    socket.on('task_deleted', (deletedTask) => {
      // Note: deletedTask might only contain ID depending on how SQLAlchemy serializes deleted objects,
      // but usually we just need the ID.
      setTasks((prev) => prev.filter((t) => t.id !== deletedTask.id));
    });

    // Ascolta i nuovi commenti per aggiornare il modale se aperto
    socket.on('comment_created', (newComment) => {
      // L'evento viene gestito all'interno del TaskDetailModal se attivo,
      // ma potremmo voler aggiornare un contatore sulla card in futuro.
      // Per ora lasciamo che il modale gestisca la sua lista.
    });

    return () => {
      socket.disconnect();
    };
  }, [id]);

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (!over || active.id === over.id) {
      return;
    }

    const activeTask = tasks.find((t) => t.id === active.id);
    const overTask = tasks.find((t) => t.id === over.id);

    // Scenario 1: Reordering within the same column
    if (activeTask && overTask && activeTask.status === overTask.status) {
      setTasks((currentTasks) => {
        const oldIndex = currentTasks.findIndex((t) => t.id === active.id);
        const newIndex = currentTasks.findIndex((t) => t.id === over.id);
        if (oldIndex === -1 || newIndex === -1) return currentTasks;
        return arrayMove(currentTasks, oldIndex, newIndex);
      });
      return;
    }

    // Scenario 2: Moving to a different column
    const overIsColumn = String(over.id).startsWith('column-');
    const newStatus = overIsColumn
      ? String(over.id).replace('column-', '')
      : overTask?.status;

    if (activeTask && newStatus && activeTask.status !== newStatus) {
      const originalStatus = activeTask.status;
      // Optimistic UI update
      setTasks((currentTasks) =>
        currentTasks.map((t) =>
          t.id === active.id ? { ...t, status: newStatus } : t
        )
      );

      // Persist change to backend
      apiFetch(`/project-tasks/${active.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      }).catch(() => {
        // Revert on error
        setTasks((currentTasks) => currentTasks.map((t) => (t.id === active.id ? { ...t, status: originalStatus } : t)));
      });
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Sei sicuro di voler eliminare questo task?")) return;
    try {
      const res = await apiFetch(`/project-tasks/${taskId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setTasks(prevTasks => prevTasks.filter(t => t.id !== taskId));
      } else {
        alert("Errore durante l'eliminazione");
      }
    } catch (error) {
      console.error("Failed to delete task", error);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...newTask, project_id: parseInt(id) };
      if (!payload.assigned_to_id) delete payload.assigned_to_id;
      else payload.assigned_to_id = parseInt(payload.assigned_to_id);

      const res = await apiFetch('/project-tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const createdTask = await res.json();
        setTasks([...tasks, createdTask]);
        setShowTaskModal(false);
        setNewTask({ name: '', description: '', status: 'todo', due_date: '', assigned_to_id: '' });
      } else {
        alert("Errore durante la creazione del task");
      }
    } catch (error) {
      console.error("Failed to create task", error);
    }
  };

  if (isLoading) {
    return <Layout><div className="p-4">Caricamento...</div></Layout>;
  }

  return (
    <Layout>
      <div className="p-4">
        <nav aria-label="breadcrumb">
          <ol className="breadcrumb">
            <li className="breadcrumb-item"><Link to="/projects">Progetti</Link></li>
            <li className="breadcrumb-item active" aria-current="page">{project?.name}</li>
          </ol>
        </nav>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="mb-0">Kanban Board: {project?.name}</h2>
          <button className="btn btn-primary" onClick={() => setShowTaskModal(true)}>+ Nuovo Task</button>
        </div>
        <DndContext onDragEnd={handleDragEnd} collisionDetection={closestCorners}>
          <div className="d-flex gap-3" style={{ overflowX: 'auto' }}>
            {TASK_STATUSES.map(status => (
              <KanbanColumn 
                key={status} 
                id={`column-${status}`} 
                title={STATUS_LABELS[status]} 
                tasks={getTasksByStatus(status)} 
                onDeleteTask={handleDeleteTask}
                onTaskClick={setSelectedTask}
              />
            ))}
          </div>
        </DndContext>

        {showTaskModal && (
          <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Nuovo Task</h5>
                  <button type="button" className="btn-close" onClick={() => setShowTaskModal(false)}></button>
                </div>
                <form onSubmit={handleCreateTask}>
                  <div className="modal-body">
                    <div className="mb-3">
                      <label className="form-label">Titolo</label>
                      <input 
                        type="text" 
                        className="form-control" 
                        required 
                        value={newTask.name}
                        onChange={(e) => setNewTask({...newTask, name: e.target.value})}
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Descrizione</label>
                      <textarea 
                        className="form-control" 
                        rows="3"
                        value={newTask.description}
                        onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                      ></textarea>
                    </div>
                    <div className="row">
                      <div className="col-md-6 mb-3">
                          <label className="form-label">Stato</label>
                          <select 
                              className="form-select"
                              value={newTask.status}
                              onChange={(e) => setNewTask({...newTask, status: e.target.value})}
                          >
                              {TASK_STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                          </select>
                      </div>
                      <div className="col-md-6 mb-3">
                          <label className="form-label">Scadenza</label>
                          <input 
                              type="date" 
                              className="form-control"
                              value={newTask.due_date}
                              onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                          />
                      </div>
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Assegna a</label>
                      <select 
                          className="form-select"
                          value={newTask.assigned_to_id}
                          onChange={(e) => setNewTask({...newTask, assigned_to_id: e.target.value})}
                      >
                          <option value="">Nessuno</option>
                          {users.map(u => (
                              <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
                          ))}
                      </select>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button type="button" className="btn btn-secondary" onClick={() => setShowTaskModal(false)}>Annulla</button>
                    <button type="submit" className="btn btn-primary">Crea</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {selectedTask && (
          <TaskDetailModal 
            task={selectedTask} 
            onClose={() => setSelectedTask(null)} 
          />
        )}
      </div>
    </Layout>
  );
}

const KanbanColumn = React.memo(function KanbanColumn({ id, title, tasks, onDeleteTask, onTaskClick }) {
  const parentRef = useRef(null);

  const rowVirtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: useCallback(() => 125, []), // Estimate card height + gap
    overscan: 5,
  });

  return (
    <div id={id} className="bg-light rounded p-2 d-flex flex-column" style={{ width: '320px', flexShrink: 0, height: 'calc(100vh - 150px)' }}>
      <h5 className="p-2">{title} <span className="badge bg-secondary rounded-pill">{tasks.length}</span></h5>
      <div ref={parentRef} style={{ flex: 1, overflowY: 'auto' }}>
        {tasks.length > 0 ? (
          <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, width: '100%', position: 'relative' }}>
            <SortableContext items={tasks.map(t => t.id)}>
              {rowVirtualizer.getVirtualItems().map(virtualItem => {
                const task = tasks[virtualItem.index];
                return (
                  <div
                    key={task.id}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: `${virtualItem.size}px`,
                      transform: `translateY(${virtualItem.start}px)`,
                      padding: '4px 2px' // to simulate gap
                    }}
                  >
                    <TaskCard task={task} onDelete={() => onDeleteTask(task.id)} onClick={() => onTaskClick(task)} />
                  </div>
                );
              })}
            </SortableContext>
          </div>
        ) : (
          // Placeholder for empty columns to remain droppable
          <div style={{ minHeight: '100px' }}></div>
        )}
      </div>
    </div>
  );
});

const TaskCard = React.memo(function TaskCard({ task, onDelete, onClick }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    cursor: 'grab',
  };

  const assignedUser = task.assigned_to;

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} onClick={onClick}>
      <div className="card shadow-sm">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start">
            <p className="fw-bold mb-1">{task.name}</p>
            <button 
              className="btn btn-sm btn-outline-danger py-0 px-2" 
              onClick={onDelete}
              onPointerDown={(e) => e.stopPropagation()} // Prevents drag start
              title="Elimina"
            >
              &times;
            </button>
          </div>
          <p className="small text-muted">{task.description}</p>
          <div className="d-flex justify-content-between align-items-center mt-2">
            <small className="text-muted">
              {task.due_date ? `Scadenza: ${new Date(task.due_date).toLocaleDateString()}` : ''}
            </small>
            {assignedUser && (
              <img
                src={assignedUser.avatar_url || `https://ui-avatars.com/api/?name=${assignedUser.full_name}&background=random`}
                alt={assignedUser.full_name}
                className="rounded-circle"
                width="24"
                height="24"
                title={assignedUser.full_name}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

function TaskDetailModal({ task, onClose }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const { user } = useAuth();
  const commentsEndRef = useRef(null);

  useEffect(() => {
    // Carica commenti iniziali
    apiFetch(`/task-comments?task_id=${task.id}`)
      .then(res => res.json())
      .then(setComments)
      .catch(console.error);

    // Setup socket listener locale per questo modale
    const socket = io(BASE_URL);
    socket.emit('join', { room: `project_${task.project_id}` });
    
    socket.on('comment_created', (comment) => {
      if (comment.task_id === task.id) {
        setComments(prev => [...prev, comment]);
        // Scroll to bottom
        setTimeout(() => commentsEndRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
      }
    });

    return () => socket.disconnect();
  }, [task.id, task.project_id]);

  const handleSendComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await apiFetch('/task-comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newComment, task_id: task.id })
      });
      setNewComment('');
    } catch (err) {
      console.error("Failed to send comment", err);
    }
  };

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content" style={{ height: '80vh' }}>
          <div className="modal-header">
            <h5 className="modal-title">{task.name}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body d-flex flex-column">
            <div className="mb-4">
              <h6>Descrizione</h6>
              <p className="text-muted">{task.description || "Nessuna descrizione."}</p>
            </div>
            <hr />
            <h6 className="mb-3">Commenti</h6>
            <div className="flex-grow-1 overflow-auto bg-light p-3 rounded mb-3">
              {comments.length === 0 && <p className="text-center text-muted small">Nessun commento ancora.</p>}
              {comments.map(c => (
                <div key={c.id} className={`d-flex mb-3 ${c.user?.id === user?.id ? 'justify-content-end' : ''}`}>
                  <div className={`card ${c.user?.id === user?.id ? 'bg-primary text-white' : 'bg-white'}`} style={{ maxWidth: '75%' }}>
                    <div className="card-body p-2">
                      <small className={`d-block fw-bold mb-1 ${c.user?.id === user?.id ? 'text-white-50' : 'text-muted'}`}>
                        {c.user?.full_name || 'Utente'} - {new Date(c.created_at).toLocaleString()}
                      </small>
                      {c.content}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={commentsEndRef} />
            </div>
            <form onSubmit={handleSendComment} className="d-flex gap-2">
              <input type="text" className="form-control" placeholder="Scrivi un commento..." value={newComment} onChange={e => setNewComment(e.target.value)} />
              <button type="submit" className="btn btn-primary">Invia</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectDetail;