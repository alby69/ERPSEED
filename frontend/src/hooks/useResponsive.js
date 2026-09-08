import { Grid } from 'antd';

const { useBreakpoint } = Grid;

/**
 * Custom hook providing responsive viewport indicators based on Ant Design breakpoints.
 * @returns {Object} { isMobile, isTablet, isDesktop, screens }
 */
export const useResponsive = () => {
    const screens = useBreakpoint();

    const isMobile = !screens.md; // < 768px
    const isTablet = !!(screens.md && !screens.lg); // 768px <= x < 992px
    const isDesktop = !!screens.lg; // >= 992px

    return {
        isMobile,
        isTablet,
        isDesktop,
        screens,
    };
};

export default useResponsive;
