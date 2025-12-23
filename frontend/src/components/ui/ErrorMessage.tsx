interface ErrorMessageProps {
  message: string;
  className?: string;
}

export function ErrorMessage({ message, className = "" }: ErrorMessageProps) {
  return (
    <p className={`text-sm text-red-500 ${className}`.trim()}>
      Error: {message}
    </p>
  );
}
