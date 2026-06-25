import { Variants, Transition } from 'framer-motion';

export const easeOutExpo: Transition = { duration: 0.8, ease: [0.16, 1, 0.3, 1] };
export const easeInExpo: Transition = { duration: 0.5, ease: [0.7, 0, 0.84, 0] };
export const easeDefault: Transition = { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] };

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: easeOutExpo },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.5 } },
};

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1, delayChildren: 0.1 },
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: easeDefault },
};

export const slideRight: Variants = {
  hidden: { opacity: 0, x: -30 },
  visible: { opacity: 1, x: 0, transition: easeOutExpo },
};

export const slideLeft: Variants = {
  hidden: { opacity: 0, x: 30 },
  visible: { opacity: 1, x: 0, transition: easeOutExpo },
};

export const cardHover = {
  whileHover: {
    y: -4,
    borderColor: 'rgba(232,168,48,0.25)',
    boxShadow: '0 8px 30px rgba(0,0,0,0.3)',
    transition: { duration: 0.25 },
  },
};

export const modalBackdrop: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.25 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

export const modalContent: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, scale: 0.95, transition: { duration: 0.2 } },
};

export const pageTransition: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, transition: { duration: 0.25 } },
};

export const countUp = (end: number, duration = 1.5) => ({
  hidden: { count: 0 },
  visible: { count: end, transition: { duration, ease: [0.16, 1, 0.3, 1] } },
});
