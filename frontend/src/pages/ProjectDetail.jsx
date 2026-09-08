import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { DndContext, closestCorners } from '@dnd-kit/core';
import { SortableContext, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useVirtualizer } from '@tanstack/react-virtual';
import { io } from 'socket.io-client';
import {
  Breadcrumb, Typography, Button, Modal, Form, Input, Select, DatePicker,
  Card, Avatar, Badge, Space, Flex, Popconfirm, message, Spin, Divider
} from 'antd';
import { PlusOutlined, DeleteOutlined, UserOutlined, SendOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

import { Layout } from '../components';
import { useAuth } from '../context';
import { formatDateForDisplay } from '@/utils/dateUtils';
import { apiFetch, BASE_URL } from '../utils';

const { Title, Text } = Typography;
const { Option } = Select;

const TASK_STATUSES = ['todo', 'in_progress', 'review', 'done'];
const STATUS_LABELS = {
  todo: 'To Do',
  in_progress: 'In Progress',
  review: 'In Review',
  done: 'Completed'
};

function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [users, setUsers] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const projectRes = await apiFetch(`/projects/${id}`);
        const projectData = await projectRes.json();
        setProject(projectData);

        const tasksRes = await apiFetch(`/project-tasks?projectId=${id}&per_page=1000`);
        const tasksData = await tasksRes.json();
        setTasks(Array.isArray(tasksData) ? tasksData : (tasksData.items || []));

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
      setTasks((prev) => prev.filter((t) => t.id !== deletedTask.id));
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

    if (activeTask && overTask && activeTask.status === overTask.status) {
      setTasks((currentTasks) => {
        const oldIndex = currentTasks.findIndex((t) => t.id === active.id);
        const newIndex = currentTasks.findIndex((t) => t.id === over.id);
        if (oldIndex === -1 || newIndex === -1) return currentTasks;
        return arrayMove(currentTasks, oldIndex, newIndex);
      });
      return;
    }

    const overIsColumn = String(over.id).startsWith('column-');
    const newStatus = overIsColumn
      ? String(over.id).replace('column-', '')
      : overTask?.status;

    if (activeTask && newStatus && activeTask.status !== newStatus) {
      const originalStatus = activeTask.status;
      setTasks((currentTasks) =>
        currentTasks.map((t) =>
          t.id === active.id ? { ...t, status: newStatus } : t
        )
      );

      apiFetch(`/project-tasks/${active.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      }).catch(() => {
        setTasks((currentTasks) => currentTasks.map((t) => (t.id === active.id ? { ...t, status: originalStatus } : t)));
      });
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      const res = await apiFetch(`/project-tasks/${taskId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        message.success("Task deleted");
        setTasks(prevTasks => prevTasks.filter(t => t.id !== taskId));
      } else {
        message.error("Error during deletion");
      }
    } catch (error) {
      console.error("Failed to delete task", error);
      message.error("Failed to delete task");
    }
  };

  const handleCreateTask = async (values) => {
    try {
      const payload = {
        name: values.name,
        description: values.description || '',
        status: values.status || 'todo',
        due_date: values.due_date ? values.due_date.format('YYYY-MM-DD') : null,
        project_id: parseInt(id)
      };
      if (values.assigned_to_id) {
        payload.assigned_to_id = parseInt(values.assigned_to_id);
      }

      const res = await apiFetch('/project-tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const createdTask = await res.json();
        setTasks([...tasks, createdTask]);
        setShowTaskModal(false);
        form.resetFields();
        message.success("Task created successfully");
      } else {
        message.error("Error creating task");
      }
    } catch (error) {
      console.error("Failed to create task", error);
      message.error("Failed to create task");
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <Flex justify="center" align="center" style={{ minHeight: '60vh' }}>
          <Spin size="large" tip="Loading project..." />
        </Flex>
      </Layout>
    );
  }

  return (
    <Layout>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Breadcrumb
          items={[
            { title: <Link to="/projects">Projects</Link> },
            { title: project?.name || 'Project' }
          ]}
        />

        <Flex justify="space-between" align="center">
          <Title level={3} style={{ margin: 0 }}>
            Kanban Board: {project?.name}
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              form.resetFields();
              setShowTaskModal(true);
            }}
          >
            New Task
          </Button>
        </Flex>

        <DndContext onDragEnd={handleDragEnd} collisionDetection={closestCorners}>
          <Flex gap="md" style={{ overflowX: 'auto', paddingBottom: 16 }}>
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
          </Flex>
        </DndContext>

        <Modal
          title="New Task"
          open={showTaskModal}
          onCancel={() => setShowTaskModal(false)}
          footer={null}
          destroyOnClose
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateTask}
            initialValues={{ status: 'todo' }}
          >
            <Form.Item name="name" label="Title" rules={[{ required: true, message: 'Please enter a task title' }]}>
              <Input placeholder="Task title" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea rows={3} placeholder="Task description..." />
            </Form.Item>
            <Flex gap="middle">
              <Form.Item name="status" label="Status" style={{ flex: 1 }}>
                <Select>
                  {TASK_STATUSES.map(s => (
                    <Option key={s} value={s}>{STATUS_LABELS[s]}</Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item name="due_date" label="Due Date" style={{ flex: 1 }}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Flex>
            <Form.Item name="assigned_to_id" label="Assign to">
              <Select allowClear placeholder="Select team member">
                {users.map(u => (
                  <Option key={u.id} value={u.id}>
                    {u.first_name} {u.last_name} ({u.email})
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Space>
                <Button onClick={() => setShowTaskModal(false)}>Cancel</Button>
                <Button type="primary" htmlType="submit">Create</Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {selectedTask && (
          <TaskDetailModal
            task={selectedTask}
            onClose={() => setSelectedTask(null)}
          />
        )}
      </Space>
    </Layout>
  );
}

const KanbanColumn = React.memo(function KanbanColumn({ id, title, tasks, onDeleteTask, onTaskClick }) {
  const parentRef = useRef(null);

  const rowVirtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: useCallback(() => 125, []),
    overscan: 5,
  });

  return (
    <Card
      id={id}
      size="small"
      style={{
        width: 320,
        minWidth: 320,
        height: 'calc(100vh - 200px)',
        background: '#fafafa',
        display: 'flex',
        flexDirection: 'column'
      }}
      styles={{
        body: {
          display: 'flex',
          flexDirection: 'column',
          flex: 1,
          padding: 12,
          overflow: 'hidden'
        }
      }}
    >
      <Flex justify="space-between" align="center" style={{ marginBottom: 12 }}>
        <Text bold style={{ fontSize: 16 }}>{title}</Text>
        <Badge count={tasks.length} overflowCount={999} style={{ backgroundColor: '#8c8c8c' }} />
      </Flex>
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
                      padding: '4px 2px'
                    }}
                  >
                    <TaskCard task={task} onDelete={() => onDeleteTask(task.id)} onClick={() => onTaskClick(task)} />
                  </div>
                );
              })}
            </SortableContext>
          </div>
        ) : (
          <div style={{ minHeight: 100 }} />
        )}
      </div>
    </Card>
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
      <Card size="small" hoverable style={{ borderRadius: 6 }}>
        <Flex justify="space-between" align="start">
          <Text strong style={{ fontSize: 14 }}>{task.name}</Text>
          <Popconfirm
            title="Delete task?"
            onConfirm={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            onCancel={(e) => e.stopPropagation()}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="text"
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
            />
          </Popconfirm>
        </Flex>
        {task.description && (
          <Text type="secondary" ellipsis={{ rows: 2 }} style={{ display: 'block', marginTop: 4, fontSize: 12 }}>
            {task.description}
          </Text>
        )}
        <Flex justify="space-between" align="center" style={{ marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 11 }}>
            {task.due_date ? `Due: ${formatDateForDisplay(task.due_date)}` : ''}
          </Text>
          {assignedUser && (
            <Avatar
              size="small"
              src={assignedUser.avatar_url}
              icon={<UserOutlined />}
              title={assignedUser.full_name}
            />
          )}
        </Flex>
      </Card>
    </div>
  );
});

function TaskDetailModal({ task, onClose }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const { user } = useAuth();
  const commentsEndRef = useRef(null);

  useEffect(() => {
    apiFetch(`/task-comments?task_id=${task.id}`)
      .then(res => res.json())
      .then(data => setComments(Array.isArray(data) ? data : (data.items || [])))
      .catch(console.error);

    const socket = io(BASE_URL);
    socket.emit('join', { room: `project_${task.project_id}` });

    socket.on('comment_created', (comment) => {
      if (comment.task_id === task.id) {
        setComments(prev => [...prev, comment]);
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
    <Modal
      title={task.name}
      open={true}
      onCancel={onClose}
      footer={null}
      width={700}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>Description</Text>
          <div>
            <Text>{task.description || "No description provided."}</Text>
          </div>
        </div>

        <Divider style={{ margin: '8px 0' }} />

        <Text strong>Comments</Text>

        <div style={{ maxHeight: 300, overflowY: 'auto', background: '#f5f5f5', padding: 12, borderRadius: 6 }}>
          {comments.length === 0 && <Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>No comments yet.</Text>}
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            {comments.map(c => {
              const isSelf = c.user?.id === user?.id;
              return (
                <Flex key={c.id} justify={isSelf ? 'end' : 'start'}>
                  <Card
                    size="small"
                    style={{
                      maxWidth: '80%',
                      background: isSelf ? '#1677ff' : '#ffffff',
                      color: isSelf ? '#ffffff' : 'inherit'
                    }}
                    styles={{ body: { padding: '8px 12px' } }}
                  >
                    <Text
                      style={{
                        fontSize: 11,
                        display: 'block',
                        marginBottom: 4,
                        color: isSelf ? 'rgba(255,255,255,0.85)' : '#8c8c8c'
                      }}
                    >
                      {c.user?.full_name || 'User'} - {new Date(c.created_at).toLocaleString()}
                    </Text>
                    <Text style={{ color: isSelf ? '#ffffff' : 'inherit' }}>
                      {c.content}
                    </Text>
                  </Card>
                </Flex>
              );
            })}
            <div ref={commentsEndRef} />
          </Space>
        </div>

        <form onSubmit={handleSendComment}>
          <Flex gap="small">
            <Input
              placeholder="Write a comment..."
              value={newComment}
              onChange={e => setNewComment(e.target.value)}
            />
            <Button type="primary" htmlType="submit" icon={<SendOutlined />}>
              Send
            </Button>
          </Flex>
        </form>
      </Space>
    </Modal>
  );
}

export default ProjectDetail;
