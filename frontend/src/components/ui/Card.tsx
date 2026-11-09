type CardProps = React.HTMLAttributes<HTMLDivElement> & {
  color?: string;
};


export default function Card({ className = "", children }: CardProps) {
  return (
    <div className={`p-6 ${className}`}>
      {children}
    </div>
  );
}