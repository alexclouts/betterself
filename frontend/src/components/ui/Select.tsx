type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement> & {
  className?: string;
};

export default function Select({ className, ...props }: SelectProps) {
  return (
    <select 
        className={`w-full rounded-l placeholder:text-muted border border-border bg-surface-raised p-3 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/30 ${className}`}
        {...props} />
  );
}