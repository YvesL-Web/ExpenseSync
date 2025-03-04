import Link from "next/link";
import React from "react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative p-6 bg-white z-1 dark:bg-gray-900 sm:p-0">
      <div className="relative flex lg:flex-row w-full h-screen justify-center flex-col  dark:bg-gray-900 sm:p-0">
        {children}
        <div className="lg:w-1/2 w-full h-full bg-brand-950 dark:bg-white/5 lg:grid items-center hidden relative">
          {/* Ajouter l'image en arrière-plan */}
          <div
            className="absolute inset-0 bg-cover bg-center z-0 bg-gradient-to-r from-RustEffect to-BabaGanoush animate-gradient "
            // backgroundImage: "url(/images/side-login.jpg)",
          ></div>

          <div className="relative items-center justify-center flex z-1">
            <div className="flex flex-col items-center max-w-xs">
              <div className="flex items-center flex-row bg-slate-950  p-4 rounded-xl">
                <p className="h2-bold text-3xl text-white text-center rounded-lg">
                  Expense<span className="gradient-title">Sync</span>
                </p>
              </div>
              <Link href="/" className="block mb-4"></Link>
              <p className="text-center text-xl font-bold text-white dark:text-black/80">
                Take control of your finances.
              </p>
            </div>
          </div>
        </div>
        <div className="fixed bottom-6 right-6 z-50 hidden sm:block bg-black rounded-full text-white "></div>
      </div>
    </div>
  );
}
