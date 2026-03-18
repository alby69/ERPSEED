// Navigation System - Main Export
// This module provides a reusable navigation system for the entire application

// Core Components
export { default as MenuBuilder } from './MenuBuilder';
export { default as AppSidebar } from './AppSidebar';
export { 
  default as Sidebar,
  AppSidebar as NewSidebar 
} from './AppSidebar';

// Provider
export { NavigationProvider, useNavigation } from './NavigationProvider';

// Constants and utilities
export { 
  DEFAULT_NAVIGATIONS,
  PERMISSION_LEVELS,
  DEFAULT_ICONS,
  NAV_ITEM_TYPES,
  hasPermission,
} from './constants';

// CSS
import './Navigation.css';
