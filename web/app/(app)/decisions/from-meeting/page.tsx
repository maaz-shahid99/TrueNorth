import { MeetingExtractor } from "@/components/meeting/MeetingExtractor";

export default function FromMeetingPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">From meeting</h1>
        <p className="text-sm text-muted">
          Paste a meeting transcript to extract the decisions that were made, then review and
          send each one to judgment (MI-2). Nothing is judged automatically.
        </p>
      </div>
      <MeetingExtractor />
    </div>
  );
}
