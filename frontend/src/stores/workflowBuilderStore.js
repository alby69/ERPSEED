import { create } from 'zustand';
import {
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  MarkerType,
} from '@xyflow/react';

const initialNodes = [
  {
    id: '1',
    type: 'trigger',
    position: { x: 250, y: 50 },
    data: { 
      label: 'Trigger',
      triggerEvent: 'order.created'
    },
  },
];

const initialEdges = [];

export const useWorkflowBuilderStore = create((set, get) => ({
  nodes: initialNodes,
  edges: initialEdges,
  
  workflowId: null,
  workflowName: '',
  workflowDescription: '',
  triggerEvent: 'order.created',
  
  selectedNode: null,
  
  setWorkflowMeta: (meta) => set({
    workflowId: meta.id || null,
    workflowName: meta.name || '',
    workflowDescription: meta.description || '',
    triggerEvent: meta.triggerEvent || 'order.created',
  }),
  
  setTriggerEvent: (event) => set({ triggerEvent: event }),
  
  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  
  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  
  onConnect: (connection) => {
    const edge = {
      ...connection,
      type: 'smoothstep',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      data: {
        branch: 'true',
      },
    };
    set({
      edges: addEdge(edge, get().edges),
    });
  },
  
  addNode: (type, position) => {
    const id = `${type}-${Date.now()}`;
    const newNode = {
      id,
      type,
      position,
      data: getDefaultNodeData(type),
    };
    set({ nodes: [...get().nodes, newNode] });
    return id;
  },
  
  updateNodeData: (nodeId, data) => {
    set({
      nodes: get().nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: { ...node.data, ...data },
          };
        }
        return node;
      }),
    });
  },
  
  deleteNode: (nodeId) => {
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      ),
      selectedNode: get().selectedNode?.id === nodeId ? null : get().selectedNode,
    });
  },
  
  selectNode: (node) => {
    set({ selectedNode: node });
  },
  
  clearSelection: () => {
    set({ selectedNode: null });
  },
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  toWorkflowConfig: () => {
    const { nodes, edges, workflowName, workflowDescription, triggerEvent } = get();
    
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    
    const stepEdges = edges.filter(e => 
      nodeMap.has(e.source) && nodeMap.has(e.target)
    );
    
    const steps = nodes
      .filter(n => n.type !== 'trigger')
      .map((node, index) => {
        const outEdges = stepEdges.filter(e => e.source === node.id);
        
        return {
          id: node.id,
          name: node.data.label || node.type,
          step_type: node.type,
          order: index,
          config: extractNodeConfig(node),
          on_true: outEdges
            .filter(e => e.data?.branch === 'true')
            .map(e => e.target),
          on_false: outEdges
            .filter(e => e.data?.branch === 'false')
            .map(e => e.target),
        };
      });
    
    return {
      name: workflowName,
      description: workflowDescription,
      trigger_event: triggerEvent,
      steps,
    };
  },
  
  loadFromWorkflow: (workflow, steps) => {
    const nodes = [];
    const edges = [];
    
    nodes.push({
      id: 'trigger',
      type: 'trigger',
      position: { x: 250, y: 50 },
      data: {
        label: 'Trigger',
        triggerEvent: workflow.trigger_event,
      },
    });
    
    const stepNodes = [];
    let yOffset = 200;
    steps.forEach((step, index) => {
      const nodeId = step.id?.toString() || `step-${index}`;
      stepNodes.push(nodeId);
      
      nodes.push({
        id: nodeId,
        type: step.step_type,
        position: { x: 250, y: yOffset },
        data: {
          label: step.name,
          ...step.config,
        },
      });
      
      edges.push({
        id: `e-trigger-${nodeId}`,
        source: 'trigger',
        target: nodeId,
        type: 'smoothstep',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
      });
      
      yOffset += 150;
    });
    
    steps.forEach((step, index) => {
      const sourceId = step.id?.toString() || `step-${index}`;
      
      (step.on_true || []).forEach(targetId => {
        edges.push({
          id: `e-${sourceId}-${targetId}-true`,
          source: sourceId,
          target: targetId,
          type: 'smoothstep',
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed },
          data: { branch: 'true' },
          label: 'True',
        });
      });
      
      (step.on_false || []).forEach(targetId => {
        edges.push({
          id: `e-${sourceId}-${targetId}-false`,
          source: sourceId,
          target: targetId,
          type: 'smoothstep',
          markerEnd: { type: MarkerType.ArrowClosed },
          data: { branch: 'false' },
          label: 'False',
        });
      });
    });
    
    set({
      workflowId: workflow.id,
      workflowName: workflow.name,
      workflowDescription: workflow.description || '',
      triggerEvent: workflow.trigger_event,
      nodes,
      edges,
    });
  },
  
  reset: () => {
    set({
      nodes: initialNodes,
      edges: initialEdges,
      workflowId: null,
      workflowName: '',
      workflowDescription: '',
      triggerEvent: 'order.created',
      selectedNode: null,
    });
  },
}));

function getDefaultNodeData(type) {
  switch (type) {
    case 'condition':
      return { label: 'Condition', field: '', operator: 'equals', value: '' };
    case 'action':
      return { label: 'Action', actionType: 'set_field', field: '', value: '' };
    case 'notification':
      return { label: 'Notification', notificationType: 'email', to: '', subject: '' };
    case 'delay':
      return { label: 'Delay', duration: 1, unit: 'hours' };
    case 'webhook':
      return { label: 'Webhook', url: '', method: 'POST' };
    default:
      return { label: 'Step' };
  }
}

function extractNodeConfig(node) {
  const { label, ...config } = node.data;
  return config;
}
