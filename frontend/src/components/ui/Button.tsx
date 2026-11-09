import React from "react";
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

function Button({ className = "", children, variant = "primary", ...props }: ButtonProps & { variant?: "primary" | "secondary" | "danger" | "ghost" }) {
  const variantClasses = {
    primary: "bg-primary text-white hover:bg-primary-dark",
    secondary: "bg-secondary text-white hover:bg-secondary-dark",
    danger: "bg-danger text-white hover:bg-red-700",
    ghost: "bg-transparent text-primary hover:bg-primary-light",
  }[variant];

  return (
    <button 
      className={`rounded-2xl p-2 shadow-sm ${variantClasses} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}


export default Button;