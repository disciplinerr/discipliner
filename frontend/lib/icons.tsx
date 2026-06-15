"use client";

import {
  Baby,
  Banknote,
  Book,
  Bus,
  Car,
  Coffee,
  CreditCard,
  Dumbbell,
  Gamepad2,
  Gift,
  GraduationCap,
  Heart,
  HeartPulse,
  House,
  type LucideIcon,
  Music,
  PawPrint,
  PiggyBank,
  Plane,
  ShoppingBag,
  ShoppingCart,
  Smartphone,
  Stethoscope,
  Tag,
  Target,
  Ticket,
  Tv,
  Utensils,
  Wallet,
  Wrench,
} from "lucide-react";

/**
 * The app's own icon set. Finance entities (categories, goals) store one of
 * these keys instead of an OS emoji, so icons render identically on every
 * platform. `AppIcon` resolves a key to its Lucide component.
 */
export const ICONS = {
  education: GraduationCap,
  housing: House,
  groceries: ShoppingCart,
  transport: Bus,
  utilities: Wrench,
  health: Stethoscope,
  dining: Utensils,
  leisure: Gamepad2,
  shopping: ShoppingBag,
  subscriptions: Tv,
  savings: PiggyBank,
  debt: CreditCard,
  target: Target,
  salary: Wallet,
  benefit: Ticket,
  money: Banknote,
  gift: Gift,
  travel: Plane,
  car: Car,
  coffee: Coffee,
  book: Book,
  fitness: Dumbbell,
  music: Music,
  heart: Heart,
  pulse: HeartPulse,
  phone: Smartphone,
  pet: PawPrint,
  baby: Baby,
  tag: Tag,
} satisfies Record<string, LucideIcon>;

export type IconKey = keyof typeof ICONS;

/** Curated subset shown in the icon picker dropdown. */
export const PICKER_ICONS: IconKey[] = [
  "target",
  "money",
  "savings",
  "salary",
  "housing",
  "groceries",
  "dining",
  "transport",
  "car",
  "travel",
  "health",
  "pulse",
  "fitness",
  "education",
  "book",
  "leisure",
  "music",
  "shopping",
  "gift",
  "coffee",
  "subscriptions",
  "phone",
  "utilities",
  "debt",
  "pet",
  "baby",
  "heart",
  "benefit",
];

/** Legacy fallback: map seeded/old emoji strings to an icon key. */
const EMOJI_TO_KEY: Record<string, IconKey> = {
  "🎓": "education",
  "🏠": "housing",
  "🛒": "groceries",
  "🚌": "transport",
  "💡": "utilities",
  "🩺": "health",
  "🍽️": "dining",
  "🎮": "leisure",
  "🛍️": "shopping",
  "📺": "subscriptions",
  "💰": "savings",
  "💳": "debt",
  "🎯": "target",
  "💸": "money",
};

export function resolveIconKey(value: string | null | undefined): IconKey {
  if (!value) return "tag";
  if (value in ICONS) return value as IconKey;
  return EMOJI_TO_KEY[value] ?? "tag";
}

export default function AppIcon({
  name,
  size = 18,
  className,
  color,
}: {
  name: string | null | undefined;
  size?: number;
  className?: string;
  color?: string;
}) {
  const Cmp = ICONS[resolveIconKey(name)];
  return <Cmp size={size} className={className} color={color} aria-hidden />;
}
