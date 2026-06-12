"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { isLoggedIn } from "@/lib/auth";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace(isLoggedIn() ? "/dashboard" : "/login");
  }, [router]);

  return null;
}
