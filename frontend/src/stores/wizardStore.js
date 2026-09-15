import { create } from 'zustand';

export const useWizardStore = create((set, get) => ({
  currentStep: 0,
  companyName: 'Mia Azienda',
  industry: 'Generico',
  hasInventory: true,
  hasPurchases: true,
  hasProjects: false,
  customDescription: '',

  nodes: [],
  edges: [],
  domainSpec: null,

  drawerOpen: false,
  selectedEntity: null,

  isAnalyzing: false,
  isProvisioning: false,
  provisionProgress: 0,
  provisionStatusText: '',

  setCurrentStep: (step) => set({ currentStep: step }),

  setFormField: (field, value) => set({ [field]: value }),

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  setDrawerOpen: (open) => set({ drawerOpen: open }),
  setSelectedEntity: (entity) => set({ selectedEntity: entity }),

  setDomainSpec: (spec) => set({ domainSpec: spec }),

  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
  setIsProvisioning: (isProvisioning) => set({ isProvisioning }),
  setProvisionProgress: (progress, statusText = '') =>
    set({ provisionProgress: progress, provisionStatusText: statusText }),

  addCustomEntity: (newEntity) => {
    const { domainSpec, nodes, edges } = get();
    if (!domainSpec) return;

    const updatedEntities = [...(domainSpec.entities || []), newEntity];
    const updatedSpec = { ...domainSpec, entities: updatedEntities };

    // Calculate position for new node
    const nodeCount = nodes.length;
    const x = (nodeCount % 3) * 280 + 50;
    const y = Math.floor(nodeCount / 3) * 200 + 50;

    const newNode = {
      id: newEntity.name,
      type: 'default',
      data: { label: `${newEntity.title} (${newEntity.name})` },
      position: { x, y },
      style: {
        background: '#e6f7ff',
        border: '2px solid #1890ff',
        borderRadius: '8px',
        padding: '12px',
        fontWeight: 'bold',
        width: 220,
      },
    };

    set({
      domainSpec: updatedSpec,
      nodes: [...nodes, newNode],
      drawerOpen: false,
      selectedEntity: null,
    });
  },

  resetWizard: () =>
    set({
      currentStep: 0,
      companyName: 'Mia Azienda',
      industry: 'Generico',
      hasInventory: true,
      hasPurchases: true,
      hasProjects: false,
      customDescription: '',
      nodes: [],
      edges: [],
      domainSpec: null,
      drawerOpen: false,
      selectedEntity: null,
      isAnalyzing: false,
      isProvisioning: false,
      provisionProgress: 0,
      provisionStatusText: '',
    }),
}));
