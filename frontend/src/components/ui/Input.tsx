type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  className?: string;
};

export default function Input({
  className = "",
  type = "text",
  placeholder = "",
  autoComplete,
  value,
  onChange,
  ...props
}: InputProps) {
  return (
    <input
      className={`w-full rounded-l placeholder:text-muted border border-border bg-surface-raised p-3 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/30 ${className}`}
      type={type}
      placeholder={placeholder}
      autoComplete={autoComplete}
      value={value}
      onChange={onChange}
      {...props}
    />
  );
}