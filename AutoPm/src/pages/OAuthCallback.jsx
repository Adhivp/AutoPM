import { useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Loader } from 'lucide-react';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const { provider } = useParams();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      // OAuth authorization failed or was cancelled
      navigate('/profile?error=oauth_failed');
      return;
    }

    if (code && provider) {
      // Redirect to profile with code and provider as query params
      navigate(`/profile?code=${code}&provider=${provider}`);
    } else {
      // Missing required parameters
      navigate('/profile?error=missing_params');
    }
  }, [navigate, provider, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <Loader className="w-12 h-12 text-primary-600 dark:text-primary-400 animate-spin mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Completing {provider} connection...
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Please wait while we connect your account.
        </p>
      </div>
    </div>
  );
};

export default OAuthCallback;
