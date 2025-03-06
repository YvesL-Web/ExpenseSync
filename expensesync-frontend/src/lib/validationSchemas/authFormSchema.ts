import * as z from "zod";

export const authFormSchema = (type: string) => z.object({
    // sign up
    firstName: type === 'sign-in' ? z.string().optional() : z.string().min(3),
    lastName: type === 'sign-in' ? z.string().optional() : z.string().min(3),
    address1: type === 'sign-in' ? z.string().optional() : z.string().max(50),
    city: type === 'sign-in' ? z.string().optional() : z.string().max(50),
    state: type === 'sign-in' ? z.string().optional() : z.string().min(2).max(2),
    postalCode: type === 'sign-in' ? z.string().optional() : z.string().min(3).max(6),
    dateOfBirth: type === 'sign-in' ? z.string().optional() : z.string().min(3),
    ssn: type === 'sign-in' ? z.string().optional() : z.string().min(3),
    re_password: type === 'sign-in' ? z.string().optional() : z.string().min(8,{message:"Confirm password must be at least 8 characters long"}),
    // both
    email: z.string().email(),
    password: z.string().min(8, { message: "Password must be at least 8 characters long" }),

  }).refine((data) => data.password === data.re_password, {
    message: "Passwords do not match",
    path:["re_password"],
})

// export const authFormSchema = (type: string) => {
//   if (type === "sign-up") {
//     return z
//       .object({
//         first_name: z
//           .string()
//           .trim()
//           .min(2, { message: "First name must be at least 2 characters long" })
//           .max(50, {
//             message: "First name must be less than 50 characters long",
//           }),
//         last_name: z
//           .string()
//           .trim()
//           .min(2, { message: "Last name must be at least 2 characters long" })
//           .max(50, {
//             message: "Last name must be less than 50 characters long",
//           }),
//         address1: z.string().nonempty("Address is required"),
//         city: z.string().nonempty("City is required"),
//         state: z.string().nonempty("State is required"),
//         postalCode: z.string().nonempty("Postal code is required"),
//         dateOfBirth: z.string().nonempty("Date of birth is required"),
//         ssn: z.string().nonempty("SSN is required"),
//         email: z.string().trim().email({message:"Enter a valid email address"}),
//         password: z
//           .string()
//           .min(6, "Password must be at least 6 characters long"),
//         re_password: z
//           .string()
//           .min(6, "Password must be at least 6 characters long"),
//       })
//       .refine((data) => data.password === data.re_password, {
//         message: "Passwords do not match",
//         path: ["re_password"],
//       });
//   } else {
//     return z.object({
//       email: z
//         .string()
//         .email("Invalid email address")
//         .nonempty("Email is required"),
//       password: z
//         .string()
//         .min(6, "Password must be at least 6 characters long"),
//     });
//   }
// };
