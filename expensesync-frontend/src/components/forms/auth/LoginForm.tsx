"use client";

import * as z from "zod";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { loginUserSchema } from "@/lib/validationSchemas";
import { useRouter } from "next/navigation";
import CustomInput from "@/components/CustomInput";
import { Loader2 } from "lucide-react";

interface FormValues {
  email: string;
  password: string;
}

const LoginForm = () => {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  // redux implementation

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<z.infer<typeof loginUserSchema>>({
    resolver: zodResolver(loginUserSchema),
    mode: "all",
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // const onSubmit = async (data: FormValues) => {
  const onSubmit = async (data: z.infer<typeof loginUserSchema>) => {
    setIsLoading(true);
    try {
      console.log(data);
    } catch (error) {
      console.log(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="auth-form">
      <header className="flex flex-col gap-5 md:gap-8">
        <Link href="/" className="cursor-pointer flex items-center gap-1 px-4">
          <Image
            src="/icons/temp-logo.svg"
            width={100}
            height={100}
            alt="Horizon logo"
          />
          <h1 className="text-26 font-ibm-plex-serif font-bold text-black-1">
            ExpenseSync
          </h1>
        </Link>
        <div className="flex flex-col gap-1 md:gap-3">
          <h1 className="text-24 lg:text-36 font-semibold text-gray-900">
            Sign In
            <p className="text-16 font-normal text-gray-600">
              {user
                ? "Link your account to get started"
                : "Please enter your details"}
            </p>
          </h1>
        </div>
      </header>
      {user ? (
        <div className="flex flex-col gap-4">{/* PlaidLink */}</div>
      ) : (
        <>
          <form className="space-y-8" onSubmit={handleSubmit(onSubmit)}>
            <CustomInput
              control={control}
              errors={errors}
              label="Email"
              name="email"
              type="email"
              placeholder="Enter your email"
            />

            <CustomInput
              control={control}
              errors={errors}
              label="Password"
              name="password"
              type="password"
              placeholder="Enter your password"
            />
            <p className="text-end mt-0">Forgot password?</p>
            <div className="flex flex-col gap-4">
              <Button
                type="submit"
                className="w-full form-btn"
                disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 size={20} className="animate-spin" /> &nbsp;
                    Loading....
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
            </div>
          </form>
          <footer className="flex justify-center gap-1">
            <p className="text-14 font-normal text-gray-600">
              Don&apos;t have an account?
            </p>
            <Link href="/register" className="form-link hover:gradient-title">
              Sign up
            </Link>
          </footer>
        </>
      )}
    </section>
  );
};
export default LoginForm;
