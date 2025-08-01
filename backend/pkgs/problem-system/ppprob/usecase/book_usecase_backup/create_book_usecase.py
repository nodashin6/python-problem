from pydddi import IUseCase, IUseCaseCommand, IUseCaseResult


class CreateBookCommand(IUseCaseCommand): ...


class CreateBookResult(IUseCaseResult): ...


class CreateBookUseCase(IUseCase[CreateBookCommand, CreateBookResult]):
    def execute(self, command: CreateBookCommand) -> CreateBookResult:
        """
        Execute the use case to create a book.

        :param command: The command containing the details for creating a book.
        :return: The result of the book creation.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
