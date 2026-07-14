import { Variants, Transition } from 'framer-motion';

// --- 1. CORE SPRINGS ---

export const transitionGentle: Transition = {
  type: 'spring',
  stiffness: 100,
  damping: 20, 
  mass: 1,
  restDelta: 0.001
};

export const transitionSnappy: Transition = {
  type: 'spring',
  stiffness: 300,
  damping: 25,
  mass: 0.8,
};

// --- 2. PAGE TRANSITIONS ---

export const pageVariants: Variants = {
  initial: { opacity: 0, y: 8 }, 
  animate: { 
    opacity: 1, 
    y: 0, 
    transition: transitionGentle 
  },
  exit: { 
    opacity: 0, 
    y: -4, 
    transition: { ...transitionGentle, duration: 0.15 } 
  },
};

// --- 3. LIST ITEM ADDITIONS ---

export const listItemVariants: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1, 
    transition: { opacity: { duration: 0.2, ease: 'easeOut' } }
  },
  exit: { 
    opacity: 0, 
    transition: transitionGentle 
  },
};

// --- 4. TACTILE HOVER/TAP STATES ---

export const hoverTactile = {
  whileHover: { 
    y: -1.5,
    transition: { type: 'tween', ease: 'easeOut', duration: 0.15 } 
  },
  whileTap: { 
    y: 0, 
    scale: 0.99,
    transition: { type: 'tween', ease: 'easeOut', duration: 0.1 } 
  }
};
