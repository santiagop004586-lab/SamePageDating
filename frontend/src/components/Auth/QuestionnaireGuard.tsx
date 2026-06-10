import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import compatibilityService from '../../services/compatibilityService';

interface QuestionnaireGuardProps {
  children: React.ReactNode;
}

/**
 * Guard that ensures user has completed the compatibility questionnaire
 * before accessing certain pages. Redirects to questionnaire if incomplete.
 */
export default function QuestionnaireGuard({ children }: QuestionnaireGuardProps) {
  const [isComplete, setIsComplete] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    checkCompletion();
  }, []);

  const checkCompletion = async () => {
    try {
      const progress = await compatibilityService.getProgress();
      setIsComplete(progress.is_complete);
    } catch (error) {
      console.error('Error checking questionnaire progress:', error);
      // If error, assume incomplete to be safe
      setIsComplete(false);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Checking your profile...</p>
        </div>
      </div>
    );
  }

  if (!isComplete) {
    return (
      <Navigate 
        to="/compatibility-questionnaire" 
        state={{ 
          from: location,
          message: "Please complete the compatibility questionnaire to continue"
        }} 
        replace 
      />
    );
  }

  return <>{children}</>;
}
