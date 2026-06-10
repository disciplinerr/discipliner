export default function Logo({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      role="img"
      aria-label="Discipliner"
    >
      <rect width="512" height="512" rx="120" fill="#0a0a0a" />
      <rect
        x="6"
        y="6"
        width="500"
        height="500"
        rx="116"
        fill="none"
        stroke="#2e2e2e"
        strokeWidth="12"
      />
      <path
        fill="#fafafa"
        fillRule="evenodd"
        d="M154 136 h84 a120 120 0 0 1 0 240 h-84 z M210 192 v128 h28 a64 64 0 0 0 0 -128 z"
      />
      <circle cx="358" cy="376" r="22" fill="#fafafa" />
    </svg>
  );
}
