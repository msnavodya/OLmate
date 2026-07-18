import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  BookOpen,
  CheckCircle2,
  Circle,
  Loader,
  RefreshCcw,
  Send,
  Sparkles,
  Trophy,
  XCircle,
} from 'lucide-react';
import { useAuth } from '../contexts/useAuth';
import { quizService, QuizResponse, QuizSubmissionResult } from '../services/quizService';
import { OL_SUBJECTS } from '../utils/constants';

const questionCounts = [3, 5, 7, 10];

export default function QuizPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [subject, setSubject] = useState(OL_SUBJECTS[0]);
  const [topic, setTopic] = useState('photosynthesis');
  const [questionCount, setQuestionCount] = useState(5);
  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<QuizSubmissionResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const answeredCount = useMemo(() => Object.keys(answers).length, [answers]);
  const totalQuestions = quiz?.questions.length || 0;
  const canSubmit = Boolean(quiz?.id && user?.id && answeredCount === totalQuestions && !result);

  const handleGenerateQuiz = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!user?.id) return;

    setIsGenerating(true);
    setError('');
    setResult(null);
    setAnswers({});

    try {
      const generatedQuiz = await quizService.generateQuiz({
        user_id: user.id,
        subject,
        topic,
        question_count: questionCount,
      });
      setQuiz(generatedQuiz);
    } catch (generateError) {
      console.error('Failed to generate quiz:', generateError);
      setError('Could not generate a quiz. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectAnswer = (questionId: string, optionIndex: number) => {
    if (result) return;
    setAnswers((previous) => ({ ...previous, [questionId]: optionIndex }));
  };

  const handleSubmitQuiz = async () => {
    if (!quiz?.id || !user?.id) return;

    setIsSubmitting(true);
    setError('');

    try {
      const submittedResult = await quizService.submitQuiz(quiz.id, {
        user_id: user.id,
        answers,
      });
      setResult(submittedResult);
    } catch (submitError) {
      console.error('Failed to submit quiz:', submitError);
      setError('Could not submit your answers. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100"
              title="Back to dashboard"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <p className="text-sm font-semibold text-amber-700">OL Mate Quiz</p>
              <h1 className="text-xl font-bold text-slate-950">Practice questions</h1>
            </div>
          </div>
          {result && (
            <div className="flex items-center gap-3 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800">
              <Trophy size={20} />
              <span className="text-sm font-bold">
                Score {result.score}/{result.total}
              </span>
            </div>
          )}
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-5 px-4 py-5 sm:px-6 lg:grid-cols-[320px_1fr] lg:px-8">
        <aside className="h-fit rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-amber-700">
              <Sparkles size={20} />
            </div>
            <div>
              <h2 className="font-bold text-slate-950">Quiz setup</h2>
              <p className="text-xs text-slate-500">Choose your revision focus</p>
            </div>
          </div>

          <form onSubmit={handleGenerateQuiz} className="space-y-4">
            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-slate-700">Subject</span>
              <select
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-sm font-semibold text-slate-950"
              >
                {OL_SUBJECTS.map((olSubject) => (
                  <option key={olSubject} value={olSubject}>
                    {olSubject}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-slate-700">Topic</span>
              <input
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-950 placeholder:text-slate-400"
                placeholder="Example: algebra, grammar, cells"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-slate-700">Questions</span>
              <select
                value={questionCount}
                onChange={(event) => setQuestionCount(Number(event.target.value))}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-sm font-semibold text-slate-950"
              >
                {questionCounts.map((count) => (
                  <option key={count} value={count}>
                    {count}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="submit"
              disabled={isGenerating}
              className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-4 font-bold text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {isGenerating ? <Loader size={18} className="animate-spin" /> : <RefreshCcw size={18} />}
              Generate quiz
            </button>
          </form>
        </aside>

        <section className="min-h-[calc(100vh-132px)]">
          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
              {error}
            </div>
          )}

          {!quiz ? (
            <div className="flex min-h-[520px] flex-col items-center justify-center rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm">
              <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-lg bg-slate-950 text-white">
                <BookOpen size={32} />
              </div>
              <h2 className="text-2xl font-bold text-slate-950">Start a practice quiz</h2>
              <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                Generate subject questions, answer them, and get instant scoring with explanations.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-amber-700">{quiz.subject}</p>
                  <h2 className="text-xl font-bold text-slate-950">{quiz.topic}</h2>
                </div>
                <div className="text-sm font-semibold text-slate-500">
                  {answeredCount}/{totalQuestions} answered
                </div>
              </div>

              {quiz.questions.map((question, questionIndex) => {
                const selectedAnswer = answers[question.id];
                const correctAnswer = result?.correct_answers[question.id] ?? question.correct_option;
                const isCorrect = result && selectedAnswer === correctAnswer;

                return (
                  <article key={question.id} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                    <div className="mb-4 flex gap-3">
                      <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-slate-950 text-sm font-bold text-white">
                        {questionIndex + 1}
                      </span>
                      <h3 className="pt-1 font-bold leading-6 text-slate-950">{question.question}</h3>
                    </div>

                    <div className="grid gap-3">
                      {question.options.map((option, optionIndex) => {
                        const isSelected = selectedAnswer === optionIndex;
                        const isCorrectOption = result && correctAnswer === optionIndex;
                        const isWrongSelection = result && isSelected && !isCorrectOption;
                        const OptionIcon = isCorrectOption ? CheckCircle2 : isWrongSelection ? XCircle : isSelected ? CheckCircle2 : Circle;

                        return (
                          <button
                            key={option}
                            onClick={() => handleSelectAnswer(question.id, optionIndex)}
                            className={getOptionClassName(Boolean(isSelected), Boolean(isCorrectOption), Boolean(isWrongSelection))}
                            disabled={Boolean(result)}
                          >
                            <OptionIcon size={19} />
                            <span>{option}</span>
                          </button>
                        );
                      })}
                    </div>

                    {result && (
                      <div className={`mt-4 rounded-lg px-4 py-3 text-sm leading-6 ${isCorrect ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'}`}>
                        {question.explanation}
                      </div>
                    )}
                  </article>
                );
              })}

              <div className="sticky bottom-0 rounded-lg border border-slate-200 bg-white p-4 shadow-lg shadow-slate-200">
                <button
                  onClick={handleSubmitQuiz}
                  disabled={!canSubmit || isSubmitting}
                  className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-cyan-600 px-4 font-bold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                >
                  {isSubmitting ? <Loader size={18} className="animate-spin" /> : <Send size={18} />}
                  Submit answers
                </button>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function getOptionClassName(isSelected: boolean, isCorrect: boolean, isWrong: boolean) {
  const baseClass = 'flex w-full items-center gap-3 rounded-lg border px-4 py-3 text-left text-sm font-semibold transition';

  if (isCorrect) {
    return `${baseClass} border-emerald-300 bg-emerald-50 text-emerald-800`;
  }

  if (isWrong) {
    return `${baseClass} border-red-300 bg-red-50 text-red-800`;
  }

  if (isSelected) {
    return `${baseClass} border-cyan-300 bg-cyan-50 text-cyan-800`;
  }

  return `${baseClass} border-slate-200 bg-slate-50 text-slate-700 hover:border-cyan-200 hover:bg-cyan-50`;
}
