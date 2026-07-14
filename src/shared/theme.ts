/** Shared source of truth for the colors that Tailwind exposes to the renderer. */
export const THEME_COLORS = {
  base: {
    bg: '#F5F2ED',
    surface: '#FCFBF9',
    border: '#E6DFD7',
  },
  text: {
    primary: '#2C2725',
    muted: '#514943',
  },
  brand: '#B94B30',
  semantic: {
    error: '#B53737',
    warning: '#966000',
    success: '#3B7051',
  },
  night: {
    bg: '#191716',
    surface: '#24211F',
    border: '#3C3633',
    text: '#EAE6E0',
    muted: '#B5AEA8',
    brand: '#E27352',
    error: '#E36A6A',
    warning: '#E6B055',
    success: '#64A37D',
  },
} as const;
