import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function base(size: number | undefined, props: SVGProps<SVGSVGElement>) {
  return {
    width: size ?? 16,
    height: size ?? 16,
    viewBox: "0 0 16 16",
    fill: "none",
    xmlns: "http://www.w3.org/2000/svg",
    "aria-hidden": true,
    ...props,
  };
}

export function IconCheck({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 8.5l3.2 3.2L13 5" />
    </svg>
  );
}

export function IconBank({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 6l6-3.5L14 6" />
      <path d="M3.5 6.5v5M6.5 6.5v5M9.5 6.5v5M12.5 6.5v5" />
      <path d="M2 13.5h12" />
    </svg>
  );
}

export function IconSpark({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} fill="currentColor">
      <path d="M8 1.5l1.2 4.1a1 1 0 00.7.7l4.1 1.2-4.1 1.2a1 1 0 00-.7.7L8 13.5l-1.2-4.1a1 1 0 00-.7-.7L2 7.5l4.1-1.2a1 1 0 00.7-.7L8 1.5z" />
    </svg>
  );
}

export function IconDot({ size, ...props }: IconProps) {
  return (
    <svg {...base(size ?? 8, props)} fill="currentColor">
      <circle cx="8" cy="8" r="4" />
    </svg>
  );
}

export function IconChevronDown({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 6l4 4 4-4" />
    </svg>
  );
}

export function IconClose({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <path d="M4 4l8 8M12 4l-8 8" />
    </svg>
  );
}

export function IconExternal({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6.5 3.5H3.5v9h9V9.5" />
      <path d="M9.5 3.5h3v3" />
      <path d="M12.5 3.5L8 8" />
    </svg>
  );
}

export function IconSend({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} fill="currentColor">
      <path d="M2 8l12-5.5-3.2 11L7.5 9.8 2 8z" stroke="currentColor" strokeWidth="1" strokeLinejoin="round" />
    </svg>
  );
}

export function IconRadar({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" fill="none">
      <circle cx="8" cy="8" r="6" />
      <circle cx="8" cy="8" r="2.5" />
      <path d="M8 8l4.5-4.5" />
      <circle cx="10.5" cy="10.5" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconHome({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none">
      <path d="M2.5 7.5L8 2.5l5.5 5" />
      <path d="M4 7v6.5h8V7" />
    </svg>
  );
}

export function IconUseful({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none">
      <path d="M4.5 7.5v5H3a1 1 0 01-1-1v-3a1 1 0 011-1h1.5zM4.5 7.5L7 2.8a1.4 1.4 0 012.6.9l-.5 2.8h2.9a1.3 1.3 0 011.3 1.6l-1 4.2a1.3 1.3 0 01-1.3 1H4.5" />
    </svg>
  );
}

export function IconNotUseful({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" style={{ transform: "rotate(180deg)" }}>
      <path d="M4.5 7.5v5H3a1 1 0 01-1-1v-3a1 1 0 011-1h1.5zM4.5 7.5L7 2.8a1.4 1.4 0 012.6.9l-.5 2.8h2.9a1.3 1.3 0 011.3 1.6l-1 4.2a1.3 1.3 0 01-1.3 1H4.5" />
    </svg>
  );
}

export function IconWrong({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" fill="none">
      <circle cx="8" cy="8" r="5.5" />
      <path d="M5.5 5.5l5 5M10.5 5.5l-5 5" />
    </svg>
  );
}
