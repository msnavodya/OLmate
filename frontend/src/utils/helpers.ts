export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function truncateText(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (
    typeof error === 'object' &&
    error !== null &&
    'request' in error &&
    !('response' in error)
  ) {
    return 'Cannot connect to the backend. Please make sure the API server is running.';
  }

  if (
    typeof error === 'object' &&
    error !== null &&
    'response' in error &&
    typeof error.response === 'object' &&
    error.response !== null &&
    'data' in error.response &&
    typeof error.response.data === 'object' &&
    error.response.data !== null &&
    'detail' in error.response.data
  ) {
    const { detail } = error.response.data;

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const firstError = detail[0];
      if (
        typeof firstError === 'object' &&
        firstError !== null &&
        'msg' in firstError &&
        typeof firstError.msg === 'string'
      ) {
        return firstError.msg;
      }
    }
  }

  return fallback;
}
