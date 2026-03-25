import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AIAssistant from '../components/ui/AIAssistant';

const AIAssistantPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [currentProjectId, setCurrentProjectId] = useState(projectId);

  useEffect(() => {
    if (!projectId) {
      const storedProjectId = localStorage.getItem('currentProjectId');
      if (storedProjectId) {
        setCurrentProjectId(storedProjectId);
      }
    }
  }, [projectId]);

  const handleClose = () => {
    navigate(-1);
  };

  const handleConfigApplied = () => {
    window.dispatchEvent(new CustomEvent('models-updated'));
  };

  return (
    <div style={{ height: '100%', padding: 0 }}>
      <AIAssistant
        visible={true}
        onClose={handleClose}
        projectId={currentProjectId}
        onConfigApplied={handleConfigApplied}
      />
    </div>
  );
};

export default AIAssistantPage;
