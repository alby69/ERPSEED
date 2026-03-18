import React, { useState, useMemo } from 'react';
import { DndContext, closestCorners } from '@dnd-kit/core';
import { SortableContext, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const KanbanCard = ({ item, titleField, descriptionField, cardColorField, cardAvatarField, cardProgressField, fields, actions, onClick }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    cursor: 'grab',
  };

  let cardClass = "card shadow-sm mb-2";
  let cardStyle = {};

  if (cardColorField && item[cardColorField]) {
     const val = item[cardColorField];
     const fieldDef = fields ? fields.find(f => f.name === cardColorField) : null;
     let color = val;
     
     if (fieldDef && fieldDef.type === 'select' && fieldDef.options) {
         try {
             const opts = JSON.parse(fieldDef.options);
             if (opts.badge_colors && opts.badge_colors[val]) {
                 color = opts.badge_colors[val];
             }
         } catch(e){}
     }
     
     if (['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'].includes(color)) {
         cardClass += ` border-start border-4 border-${color}`;
     } else if (color && color.startsWith('#')) {
         cardStyle.borderLeft = `4px solid ${color}`;
     }
  }

  let avatarUrl = null;
  let avatarName = null;

  if (cardAvatarField) {
      // L'API dinamica restituisce gli oggetti relazionati senza il suffisso _id
      // Es. assigned_to_id -> assigned_to
      const objectKey = cardAvatarField.endsWith('_id') ? cardAvatarField.slice(0, -3) : cardAvatarField;
      const relatedObj = item[objectKey];
      
      if (relatedObj) {
          if (relatedObj.avatar) {
              avatarUrl = `http://localhost:5000/uploads/${relatedObj.avatar}`;
          }
          
          const name = relatedObj.first_name 
            ? `${relatedObj.first_name} ${relatedObj.last_name}` 
            : (relatedObj.name || relatedObj.email || relatedObj.title || 'User');
            
          avatarName = name;
          if (!avatarUrl) {
              avatarUrl = `https://ui-avatars.com/api/?name=${name}&background=random`;
          }
      }
  }

  let progressBar = null;
  if (cardProgressField && item[cardProgressField] !== undefined && item[cardProgressField] !== null) {
      const val = parseFloat(item[cardProgressField]);
      if (!isNaN(val)) {
          const percent = Math.min(Math.max(val, 0), 100);
          let bgClass = 'bg-primary';
          if (percent >= 100) bgClass = 'bg-success';
          else if (percent < 30) bgClass = 'bg-danger';
          else if (percent < 70) bgClass = 'bg-warning';
          
          progressBar = (
              <div className="progress mt-2" style={{ height: '6px' }}>
                  <div 
                      className={`progress-bar ${bgClass}`} 
                      role="progressbar" 
                      style={{ width: `${percent}%` }} 
                      aria-valuenow={percent} 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                  ></div>
              </div>
          );
      }
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} onClick={() => onClick(item)}>
      <div className={cardClass} style={cardStyle}>
        <div className="card-body p-2">
          <div className="d-flex justify-content-between align-items-start">
            <p className="fw-bold mb-1 text-truncate" style={{flex: 1}}>{item[titleField] || `ID: ${item.id}`}</p>
            {avatarUrl && (
              <img 
                src={avatarUrl} 
                alt={avatarName} 
                title={avatarName}
                className="rounded-circle ms-2 border"
                style={{ width: '24px', height: '24px', objectFit: 'cover' }}
              />
            )}
          </div>
          {descriptionField && <p className="small text-muted mb-0 text-truncate">{item[descriptionField]}</p>}
          {progressBar}
          {actions && (
            <div className="mt-2 d-flex justify-content-end">{actions(item)}</div>
          )}
        </div>
      </div>
    </div>
  );
};

const KanbanColumn = ({ id, title, items, titleField, descriptionField, cardColorField, cardAvatarField, cardProgressField, columnTotalField, fields, actions, onCardClick, isCollapsed, onToggleCollapse }) => {
  const { setNodeRef } = useSortable({ id });

  if (isCollapsed) {
    return (
      <div ref={setNodeRef} className="bg-light rounded p-2 d-flex flex-column align-items-center" style={{ width: '50px', flexShrink: 0, height: 'calc(100vh - 220px)', cursor: 'pointer' }} onClick={onToggleCollapse}>
        <h6 className="p-2 text-uppercase text-muted small fw-bold" style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}>
          {title} <span className={`badge rounded-pill ${items.length > 0 ? 'bg-primary' : 'bg-secondary'}`}>{items.length}</span>
        </h6>
      </div>
    );
  }

  let columnTotal = null;
  if (columnTotalField && items.length > 0) {
    const total = items.reduce((sum, item) => {
      const value = parseFloat(item[columnTotalField]);
      return sum + (isNaN(value) ? 0 : value);
    }, 0);
    columnTotal = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(total);
  }

  return (
    <div ref={setNodeRef} className="bg-light rounded p-2 d-flex flex-column" style={{ width: '300px', flexShrink: 0, height: 'calc(100vh - 220px)' }}>
      <div className="d-flex justify-content-between align-items-center">
        <div className="p-2 text-uppercase text-muted small fw-bold mb-0 text-truncate">
          {title} 
          <span className={`badge rounded-pill ms-2 ${items.length > 0 ? 'bg-primary' : 'bg-secondary'}`}>{items.length}</span>
          {columnTotal && <span className="ms-2 badge bg-light text-dark border">{columnTotal}</span>}
        </div>
        <button 
          className="btn btn-sm btn-link text-muted py-0 px-1" 
          onClick={onToggleCollapse}
          title="Collassa colonna"
        >
          <i className="bi bi-chevron-left"></i>
        </button>
      </div>
      <div className="flex-grow-1" style={{ overflowY: 'auto' }}>
        <SortableContext items={items.map(i => i.id)}>
          {items.map(item => (
            <KanbanCard 
              key={item.id} 
              item={item} 
              titleField={titleField}
              descriptionField={descriptionField}
              cardColorField={cardColorField}
              cardAvatarField={cardAvatarField}
              cardProgressField={cardProgressField}
              fields={fields}
              actions={actions}
              onClick={onCardClick}
            />
          ))}
        </SortableContext>
      </div>
    </div>
  );
};

function KanbanView({ 
  data, 
  kanbanConfig, 
  onStatusChange,
  actions,
  onCardClick,
  persistenceKey
}) {
  const { statusField, statusValues, titleField, descriptionField, cardColorField, cardAvatarField, cardProgressField, columnTotalField, fields } = kanbanConfig;
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState('');

  // Estrae gli utenti unici dai dati per il filtro
  const uniqueUsers = useMemo(() => {
    if (!cardAvatarField) return [];
    const objectKey = cardAvatarField.endsWith('_id') ? cardAvatarField.slice(0, -3) : cardAvatarField;
    const usersMap = new Map();
    
    data.forEach(item => {
      const user = item[objectKey];
      if (user && user.id) {
        usersMap.set(user.id, user);
      }
    });
    
    return Array.from(usersMap.values());
  }, [data, cardAvatarField]);

  const [collapsedColumns, setCollapsedColumns] = useState(() => {
    if (!persistenceKey) return [];
    try {
      const saved = localStorage.getItem(persistenceKey);
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      return [];
    }
  });

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (!over) return;

    const activeItem = data.find(item => item.id === active.id);
    const overIsColumn = String(over.id).startsWith('column-');
    
    let newStatus;
    if (overIsColumn) {
      newStatus = String(over.id).replace('column-', '');
    } else {
      const overItem = data.find(item => item.id === over.id);
      if (overItem) {
        newStatus = overItem[statusField];
      }
    }

    if (activeItem && newStatus && activeItem[statusField] !== newStatus) {
      onStatusChange(active.id, newStatus);
    }
  };

  const getItemsByStatus = (status) => {
    return data.filter(item => {
      const matchesStatus = String(item[statusField]) === String(status);
      if (!matchesStatus) return false;
      
      // Filtro per Utente
      if (selectedUser && cardAvatarField) {
         const objectKey = cardAvatarField.endsWith('_id') ? cardAvatarField.slice(0, -3) : cardAvatarField;
         const user = item[objectKey];
         if (!user || String(user.id) !== String(selectedUser)) return false;
      }
      
      if (!searchTerm) return true;
      
      const title = item[titleField] ? String(item[titleField]).toLowerCase() : '';
      const desc = descriptionField && item[descriptionField] ? String(item[descriptionField]).toLowerCase() : '';
      const term = searchTerm.toLowerCase();
      
      return title.includes(term) || desc.includes(term);
    });
  };

  const toggleColumnCollapse = (columnId) => {
    setCollapsedColumns(prev => {
      const newState = prev.includes(columnId) 
        ? prev.filter(id => id !== columnId) 
        : [...prev, columnId];
      if (persistenceKey) {
        localStorage.setItem(persistenceKey, JSON.stringify(newState));
      }
      return newState;
    });
  };

  return (
    <div className="d-flex flex-column h-100">
      <div className="mb-3 d-flex gap-2">
        <input
          type="text"
          className="form-control"
          placeholder="Cerca nella Kanban..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        {cardAvatarField && uniqueUsers.length > 0 && (
          <select 
            className="form-select" 
            style={{ maxWidth: '250px' }}
            value={selectedUser} 
            onChange={(e) => setSelectedUser(e.target.value)}
          >
            <option value="">Tutti gli utenti</option>
            {uniqueUsers.map(u => {
               const name = u.first_name 
                 ? `${u.first_name} ${u.last_name}` 
                 : (u.name || u.email || u.title || 'User');
               return <option key={u.id} value={u.id}>{name}</option>;
            })}
          </select>
        )}
      </div>
      <DndContext onDragEnd={handleDragEnd} collisionDetection={closestCorners}>
        <div className="d-flex gap-3 flex-grow-1" style={{ overflowX: 'auto' }}>
          {statusValues.map(statusInfo => {
            const statusValue = typeof statusInfo === 'object' ? statusInfo.value : statusInfo;
            const statusLabel = typeof statusInfo === 'object' ? statusInfo.label : statusInfo;
            const columnId = `column-${statusValue}`;
            
            return (
              <KanbanColumn
                key={columnId}
                id={columnId}
                title={statusLabel}
                items={getItemsByStatus(statusValue)}
                titleField={titleField}
                descriptionField={descriptionField}
                cardColorField={cardColorField}
                cardAvatarField={cardAvatarField}
                cardProgressField={cardProgressField}
                columnTotalField={columnTotalField}
                fields={fields}
                actions={actions}
                onCardClick={onCardClick}
                isCollapsed={collapsedColumns.includes(columnId)}
                onToggleCollapse={() => toggleColumnCollapse(columnId)}
              />
            );
          })}
        </div>
      </DndContext>
    </div>
  );
}

export default KanbanView;